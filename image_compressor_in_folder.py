import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from functionalities.validations import validate_folder_path, validate_quality, validate_output_format

def get_validated_input(prompt, valid_options=None, default=None, validate_func=None):
    """
    Obtiene una entrada válida del usuario, con opción para salir.

    :param prompt: Mensaje para solicitar la entrada.
    :param valid_options: Opciones válidas para la entrada (puede ser una lista de cadenas).
    :param default: Valor predeterminado si el usuario no proporciona una entrada.
    :param validate_func: Función de validación adicional para la entrada.
    :return: Valor validado de la entrada.
    """
    while True:
        user_input = input(prompt).strip()
        if user_input.lower() == 'q':
            print("Saliendo del script.")
            exit()
        if not user_input and default is not None:
            return default
        if valid_options and user_input.lower() not in valid_options:
            print(f"Entrada no válida. Opciones válidas son: {', '.join(valid_options)}.")
        elif validate_func and not validate_func(user_input):
            print("Entrada no válida.")
        else:
            return user_input

def compress_image(input_path, output_path, quality=85, output_format=None, resize_factor=1.0, convert_to_grayscale=False):
    """
    Comprime una imagen para reducir su tamaño manteniendo la calidad.
    """
    try:
        with Image.open(input_path) as img:
            original_format = img.format if output_format is None else output_format
            
            # Convertir imagen si es necesario
            if convert_to_grayscale:
                img = img.convert('L')
            else:
                if original_format == 'JPEG':
                    if img.mode in ('RGBA', 'LA'):
                        img = img.convert('RGB')
                elif original_format == 'PNG':
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')

            # Redimensionar imagen
            if resize_factor != 1.0:
                width, height = img.size
                img = img.resize((int(width * resize_factor), int(height * resize_factor)), Image.Resampling.LANCZOS)

            # Guardar imagen comprimida
            if original_format == 'JPEG':
                img.save(output_path, original_format, quality=quality, optimize=True)
            elif original_format == 'PNG':
                img.save(output_path, original_format, optimize=True)
            else:
                img.save(output_path, optimize=True)

            print(f"Imagen comprimida y guardada: {output_path}")
    except Exception as e:
        print(f"Error al comprimir la imagen {input_path}: {e}")

def compress_images_in_folder(folder_path, output_folder, quality=85, output_format=None, resize_factor=1.0, convert_to_grayscale=False):
    """
    Comprime todas las imágenes en una carpeta utilizando compresión en paralelo.
    """
    supported_formats = ('.jpg', '.jpeg', '.png')
    if not validate_folder_path(folder_path):
        print(f"La carpeta de origen no existe: {folder_path}")
        return

    os.makedirs(output_folder, exist_ok=True)

    # Recopilar archivos de imagen
    image_files = [os.path.join(folder_path, filename)
                   for filename in os.listdir(folder_path)
                   if filename.lower().endswith(supported_formats)]

    # Función para determinar el formato de salida
    def get_output_file(input_file):
        ext = output_format.lower() if output_format else os.path.splitext(input_file)[1].lower()
        if ext not in supported_formats:
            ext = '.jpg' if output_format == 'JPEG' else '.png'
        return os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + ext)

    # Ejecutar compresión en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(compress_image, file, get_output_file(file), quality, output_format, resize_factor, convert_to_grayscale)
                   for file in image_files]
        for future in as_completed(futures):
            future.result()

    print(f"\nCompresión completada. Imágenes guardadas en: {output_folder}")

def validate_output_path(output_folder):
    """
    Valida si la ruta de salida es una carpeta válida para guardar las imágenes en Windows.
    """
    allowed_paths = ['Desktop', 'Downloads', 'Pictures']
    if any(os.path.join(os.path.expanduser(f"~"), path) in output_folder for path in allowed_paths):
        return True
    print(f"La ruta de salida debe estar en una de las carpetas permitidas: {', '.join(allowed_paths)}.")
    return False

if __name__ == "__main__":
    print("=== Compresor de Imágenes ===\n")

    folder_path = get_validated_input("Introduce la ruta de la carpeta con las imágenes a comprimir (o 'q' para salir): ", validate_func=validate_folder_path)
    output_folder = get_validated_input("Introduce la ruta de la carpeta de salida para las imágenes comprimidas (o 'q' para salir): ", validate_func=validate_output_path)
    quality_input = get_validated_input("Introduce el nivel de calidad para la compresión (1-100, por defecto es 85, 'q' para salir): ", validate_func=validate_quality, default="85")
    format_input = get_validated_input("Introduce el formato de salida (JPEG, PNG, mantener original - dejar en blanco, 'q' para salir): ", valid_options=["jpeg", "png", ""], default="")
    resize_input = get_validated_input("Introduce el factor de reducción de resolución (por defecto es 1.0, sin cambio): ", default="1.0")
    grayscale_option = get_validated_input("¿Convertir a escala de grises? (s/n, por defecto es 'n'): ", valid_options=["s", "n"], default="n")

    quality = validate_quality(quality_input)
    output_format = validate_output_format(format_input)
    resize_factor = float(resize_input) if resize_input else 1.0
    convert_to_grayscale = grayscale_option == 's'

    compress_images_in_folder(folder_path, output_folder, quality, output_format, resize_factor, convert_to_grayscale)