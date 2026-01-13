"""
Validadores de Input para o Viral Bot
Garantem segurança e integridade dos dados
"""

import re
import os
from typing import Tuple, Optional


def sanitize_filename(filename: str) -> str:
    """
    Remove caracteres perigosos de nomes de arquivo.
    
    Args:
        filename: Nome do arquivo a sanitizar
    
    Returns:
        Nome sanitizado, seguro para uso no sistema de arquivos
    """
    # Remover caracteres especiais perigosos
    sanitized = re.sub(r'[\\/*?:"<>|]', '', filename)
    # Limitar tamanho
    sanitized = sanitized[:50]
    # Remover espaços extras
    sanitized = sanitized.strip()
    # Substituir espaços por underscores
    sanitized = sanitized.replace(' ', '_')
    # Converter para lowercase
    sanitized = sanitized.lower()
    
    return sanitized or "default"


def validate_niche(niche: str) -> Tuple[bool, str, Optional[str]]:
    """
    Valida o nicho informado pelo usuário.
    
    Args:
        niche: Texto do nicho
    
    Returns:
        Tupla (is_valid, sanitized_niche, error_message)
    """
    if not niche or not isinstance(niche, str):
        return False, "", "Nicho não pode ser vazio"
    
    niche = niche.strip()
    
    if len(niche) < 3:
        return False, niche, "Nicho deve ter pelo menos 3 caracteres"
    
    if len(niche) > 100:
        return False, niche[:100], "Nicho truncado para 100 caracteres"
    
    # Verificar caracteres suspeitos (injeção)
    if re.search(r'[<>"\';]', niche):
        return False, "", "Nicho contém caracteres inválidos"
    
    return True, niche, None


def validate_quantity(quantity: any) -> Tuple[bool, int, Optional[str]]:
    """
    Valida a quantidade de vídeos.
    
    Args:
        quantity: Quantidade informada
    
    Returns:
        Tupla (is_valid, parsed_quantity, error_message)
    """
    try:
        qty = int(quantity)
    except (ValueError, TypeError):
        return False, 1, "Quantidade deve ser um número inteiro"
    
    if qty < 1:
        return False, 1, "Quantidade mínima é 1"
    
    if qty > 10:
        return False, 10, "Quantidade máxima é 10 (ajustado automaticamente)"
    
    return True, qty, None


def validate_request(data: dict) -> Tuple[bool, dict, list]:
    """
    Valida todo o request de geração de vídeo.
    
    Args:
        data: Dicionário com dados do request
    
    Returns:
        Tupla (is_valid, validated_data, errors)
    """
    errors = []
    validated = {}
    
    # Validar nicho
    niche = data.get('nicho', '')
    valid, sanitized, error = validate_niche(niche)
    if error:
        errors.append(error)
    validated['nicho'] = sanitized if valid else 'ai_tools'
    
    # Validar quantidade
    qty = data.get('quantidade', 5)
    valid, parsed, error = validate_quantity(qty)
    if error:
        errors.append(error)
    validated['quantidade'] = parsed
    
    # Validar useTrends (bool)
    use_trends = data.get('useTrends', True)
    validated['useTrends'] = bool(use_trends)
    
    is_valid = len([e for e in errors if 'Quantidade mínima' in e or 'vazio' in e or 'inválidos' in e]) == 0
    
    return is_valid, validated, errors


# Exportar funções
__all__ = [
    'sanitize_filename',
    'validate_niche',
    'validate_quantity',
    'validate_request'
]
