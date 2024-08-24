import os

def validate_folder_path(path):
    """
    Valida si la ruta de la carpeta existe.

    :param path: Ruta de la carpeta a validar.
    :return: Booleano que indica si la ruta es válida.
    """
    return os.path.isdir(path)

def validate_quality(value):
    """
    Valida el valor de calidad para la compresión.

    :param value: Valor de calidad a validar.
    :return: Valor de calidad si es válido, de lo contrario, None.
    """
    if value.isdigit():
        quality = int(value)
        if 1 <= quality <= 100:
            return quality
    return None

def validate_output_format(value):
    """
    Valida el formato de salida.

    :param value: Formato de salida a validar.
    :return: Formato válido si es reconocido, de lo contrario, None.
    """
    valid_formats = ['JPEG', 'PNG']
    return value.upper() if value.upper() in valid_formats else None

def validate_output_path(path):
    # Lista de carpetas válidas
    valid_folders = ['Desktop', 'Downloads', 'Images']
    
    # Obtener el directorio base desde la ruta proporcionada
    base_directory = os.path.basename(os.path.normpath(path))
    
    # Verificar si la carpeta base está en la lista de carpetas permitidas
    if base_directory in valid_folders:
        return True

    # Verificar si el path contiene alguna de las carpetas permitidas
    for folder in valid_folders:
        if folder in path.split(os.sep):
            return True

    # Si no se encuentra una carpeta válida, devolver False
    
    return False

def validate_output_path(path, carpetas_a_verificar):
    
    # Convertir la ruta a un array
    ruta_array = path.split("\\") if "\\" in path else path.split("/")
    
    # Verificar si alguna de las carpetas está en el array de la ruta
    carpetas_encontradas = [carpeta for carpeta in carpetas_a_verificar if carpeta in ruta_array]
    
    # Retornar True si se encuentra alguna carpeta, de lo contrario False
    return True if carpetas_encontradas else False