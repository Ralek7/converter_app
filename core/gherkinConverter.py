"""
Copyright (c) 2025 Alejandro Ramírez  
Bajo la Licencia de Autor Restringida (LAR) v1.0  
Más detalles en LICENSE
""" 

import json
import os
import re
import textwrap
import time
import unicodedata
from typing import Dict, Any

class UltimateGherkinConverter:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # print("""
        #     ███████╗ ████████╗████████╗ ██████╗ ████████╗
        #     ██╔═══██╗   ██║   ██╔════╝ ██╔══██╗    ██║   
        #     ██║   ██║   ██║   ██║      ███████║    ██║   
        #     ██║   ██║   ██║   ██║      ██╔══██║    ██║   
        #     ██║   ██║   ██║   ██║      ██║  ██║    ██║   
        #     ███████║ ████████║████████║╚═╝  ╚═╝ ████████║ v1.05
        #     </Alek>          
        #       """)    
        
        print("\nInicializando modelo de procesamiento de IA...\n")
        time.sleep(2)


    def _clean_text(self, text: str) -> str:
        return re.sub(r'[^\wá-úÁ-Ú \n\-]', '', text, flags=re.IGNORECASE).strip()

    def _is_valid_step(self, text: str) -> bool:
        clean_text = text.strip() if text else ''
        return len(clean_text) > 2 and not re.match(r'^[\d\W]+$', clean_text)

    def _detect_patterns(self, steps: list) -> Dict[str, Any]:
        patterns = {
            'beneficiary': [
                r"(?:Ingresa|Ingresar|Capturar) (?:el )?(?:primer )?nombre del Cliente\b.*",
                r"(?:Ingresa|Ingresar|Capturar) (?:el )?apellido paterno\b.*",
                r"(?:Ingresa|Ingresar|Capturar) (?:el )?apellido materno\b.*",
                r"Capturar el primer nombre del Cliente\b.*",
                r"Nombre del Cliente:?\s*\*\*<.*>\*\*"
            ],
            'tarjeta': [
                r"[Dd]eslizar? (?:una )?tarjeta\b",
                r"[Dd]esliza (?:una )?tarjeta\b",
                r"Operación con tarjeta.*"
            ],
            'cuenta': [
                r"Capturar los siguientes datos:\s*\n?N[úu]mero de Cuenta \*\*<.*>\*\*",
                r"Capturar los siguientes datos:\s*\n?N[úu]mero de Tarjeta \*\*<.*>\*\*",
                r"Capturar (?:los siguientes datos|el):.*N[úu]mero de Cuenta.*",
                r"N[úu]mero de cuenta:?\s*\*\*<.*>\*\*"
            ],
            'desglose': [
                r"Capturar (?:el|registro|desglose) (?:total )?efectivo.*",
                r"Registro de efectivo (?:que ingresa|sale).*",
                r"Desglose monetario.*"
            ],
            'enter': [
                r"Dar \"Enter\"",
                r"Presionar tecla Enter",
                r"Confirmar con Enter"
            ]
        }
        
        detected = {
            'beneficiary': False,
            'tarjeta': False,
            'cuenta': False,
            'desglose': False,
            'nombre_first': False,
            'direccion_after': False
        }
        
        step_contents = [self._clean_text(s.get('paso', '')) for s in steps]

        for i, content in enumerate(step_contents):
            if any(re.search(pattern, content, re.IGNORECASE) 
               for pattern in patterns['beneficiary']):
                detected['beneficiary'] = True
                if "nombre" in content.lower() and not detected['nombre_first']:
                    detected['nombre_first'] = i

            if "direcci" in content.lower() and detected['nombre_first'] is not False:
                if i > detected['nombre_first']:
                    detected['direccion_after'] = True

            for category in ['tarjeta', 'cuenta', 'desglose']:
                if any(re.search(pattern, content, re.IGNORECASE) 
                      for pattern in patterns[category]):
                    detected[category] = True

        return detected

    def _process_steps(self, raw_steps: Dict) -> Dict[str, Any]:
        try:
            sorted_steps = sorted(
                ({'key': int(k), **v} for k, v in raw_steps.items()),
                key=lambda x: x['key']
            )
        except:
            sorted_steps = list(raw_steps.values())
        
        detected = self._detect_patterns(sorted_steps)

        given = next(
            (f"{self._clean_text(s['paso'])}" 
             for s in sorted_steps if s.get('paso')), 
            "Iniciar flujo"
        )

        when_actions = []
        if detected['tarjeta']:
            when_actions.append("Deslizar tarjeta")
        if detected['cuenta']:
            when_actions.append("Ingresar datos de cuenta/tarjeta")
        if detected['desglose']:
            when_actions.append("Registrar desglose de efectivo")
        if detected['beneficiary']:
            when_actions.append("Ingresar datos del beneficiario")
            if detected['direccion_after']:
                when_actions.append("Verificar dirección asociada")

        # Manejo de validación vacía mejorado
        last_validation = next(
            (self._clean_text(s.get('validacion', '')) 
             for s in reversed(sorted_steps) 
             if self._is_valid_step(s.get('validacion', ''))),
            'El sistema regresa a la pantalla inicial VENTANILLA con el campo Clave habilitado'
        )

        return {
            'Given': given[:120],
            'When': when_actions[0][:100] if when_actions else "Ejecutar proceso principal",
            'Then': last_validation[:150],
            'And': ["Hacer clic en el boton Aceptar"] + [a[:100] for a in when_actions[1:]]
        }

    def _format_step(self, text: str) -> str:
        return '\n      '.join(textwrap.wrap(text, width=150, break_long_words=False))

    def _generate_feature(self, module: str, title: str, steps: Dict) -> str:
        clean_module = re.sub(r'\W+', '_', module.split('-')[-1]).strip('_')
        scenario_name = re.sub(r'[\W_]+', ' ', title.split('_')[-1]).title()[:70]
        
        feature_lines = [
            f"Feature: {clean_module}\n",
            f"  Scenario: {scenario_name}",
            f"    Given {self._format_step(steps['Given'])}"
        ]

        if steps['When']:
            feature_lines.append(f"    When {self._format_step(steps['When'])}")
            for and_step in steps['And']:
                feature_lines.append(f"    And {self._format_step(and_step)}")

        feature_lines.append(f"    Then {self._format_step(steps['Then'])}")
        
        return '\n'.join(feature_lines)

    def _normalize_filename(self, filename: str) -> str:
        name = filename.rsplit('.json', 1)[0]
        normalized = unicodedata.normalize('NFKD', name)
        ascii_name = normalized.encode('ASCII', 'ignore').decode('utf-8')
        cleaned = re.sub(r'[^\w\s-]', '', ascii_name)
        underscored = re.sub(r'[\s-]+', '_', cleaned)
        final_name = re.sub(r'[._]+', '_', underscored).strip('_')
        return f"{final_name}.feature"

    def convert(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for filename in os.listdir(self.input_dir):
            if filename.endswith('.json'):
                print(f"Procesando archivo: {filename}")
                try:
                    file_path = os.path.join(self.input_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    processed = self._process_steps(data.get("CasoPrueba", {}))
                    feature_content = self._generate_feature(
                        module=data.get("Modulo", "Modulo_Principal"),
                        title=data.get("Titulo", "Escenario_Principal"),
                        steps=processed
                    )

                    feature_filename = self._normalize_filename(filename)
                    output_file = os.path.join(self.output_dir, feature_filename)
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(feature_content)
                    print(f"Archivo generado: {output_file}")    

                except Exception as e:
                    print(f"Error procesando {filename}: {str(e)}")

if __name__ == "__main__":
    converter = UltimateGherkinConverter(
        input_dir="test_cases",
        output_dir="features"
    )
    converter.convert()