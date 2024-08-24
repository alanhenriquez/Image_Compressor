import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from functionalities.validations import validate_folder_path, validate_quality, validate_output_path



# Constantes
CACHE_DIR = './cache'
CARPETAS_A_VERIFICAR = ["Desktop", "Documents", "Downloads"]



# Funciones de Manejo de Caché
def create_cache_folder():
    """Crea la carpeta de caché si no existe."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def clear_cache():
    """Elimina todos los archivos en la carpeta de caché."""
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

def get_cache_file_path():
    """Devuelve la ruta del archivo de caché para la imagen comprimida temporalmente."""
    return os.path.join(CACHE_DIR, 'temp_compressed_image.jpg')



# Funciones de Compresión de Imágenes
def compress_image(input_path, output_path, quality=85, resize_factor=1.0, convert_to_grayscale=False):
    """Comprime una imagen y la guarda en el directorio de salida especificado."""
    try:
        with Image.open(input_path) as img:
            if convert_to_grayscale:
                img = img.convert('L')
            else:
                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')

            if resize_factor != 1.0:
                width, height = img.size
                img = img.resize((int(width * resize_factor), int(height * resize_factor)), Image.Resampling.LANCZOS)

            img.save(output_path, quality=quality, optimize=True)
            print(f"Imagen comprimida y guardada: {output_path}")
            return img  # Retorna la imagen comprimida
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo de entrada no se encuentra.")
    except PermissionError:
        messagebox.showerror("Error", "Permiso denegado para acceder al archivo o directorio.")
    except IOError as e:
        messagebox.showerror("Error", f"Error de entrada/salida: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado: {e}")

def compress_and_cache_image(input_path, quality=85, resize_factor=1.0, convert_to_grayscale=False):
    """Comprime una imagen y la guarda en la caché temporalmente."""
    cache_path = get_cache_file_path()
    compress_image(input_path, cache_path, quality, resize_factor, convert_to_grayscale)
    return cache_path



# Funciones de Visualización
def show_image(image_path, is_compressed=False, original_size=None):
    """Muestra una imagen en la interfaz gráfica y muestra información sobre la imagen."""
    try:
        with Image.open(image_path) as img:
            img.thumbnail((400, 400))  # Redimensionar la imagen para que quepa en el Label
            img_tk = ImageTk.PhotoImage(img)
            
            # Tamaño de archivo en KB
            file_size_kb = os.path.getsize(image_path) / 1024
            
            # Dimensiones
            dimensions = f"{img.width}x{img.height}"
            
            # Formato
            image_format = img.format

            if is_compressed:
                compressed_image_label.config(image=img_tk)
                compressed_image_label.image = img_tk
                
                if original_size is not None:
                    # Diferencia en tamaño y porcentaje de compresión
                    compressed_size_kb = file_size_kb
                    original_size_kb = original_size / 1024
                    size_reduction = original_size_kb - compressed_size_kb
                    compression_percentage = (size_reduction / original_size_kb) * 100
                    
                    compressed_image_info.set(
                        f"Tamaño: {compressed_size_kb:.2f} KB\n"
                        f"Dimensiones: {dimensions}\n"
                        f"Formato: {image_format}\n"
                        f"Reducción de tamaño: {size_reduction:.2f} KB\n"
                        f"Porcentaje de compresión: {compression_percentage:.2f}%"
                    )
                else:
                    compressed_image_info.set(
                        f"Tamaño: {file_size_kb:.2f} KB\n"
                        f"Dimensiones: {dimensions}\n"
                        f"Formato: {image_format}"
                    )
            else:
                original_image_label.config(image=img_tk)
                original_image_label.image = img_tk
                
                if original_size is not None:
                    # Asumir que la imagen es la original y no comprimida
                    original_size_kb = original_size / 1024
                    size_reduction = 0
                    compression_percentage = 0
                    
                    original_image_info.set(
                        f"Tamaño: {original_size_kb:.2f} KB\n"
                        f"Dimensiones: {dimensions}\n"
                        f"Formato: {image_format}\n"
                        f"Reducción de tamaño: {size_reduction:.2f} KB\n"
                        f"Porcentaje de compresión: {compression_percentage:.2f}%"
                    )
                else:
                    original_image_info.set(
                        f"Tamaño: {file_size_kb:.2f} KB\n"
                        f"Dimensiones: {dimensions}\n"
                        f"Formato: {image_format}"
                    )
    except Exception as e:
        print(f"Error al cargar la imagen {image_path}: {e}")



# Funciones de Interfaz Gráfica
def browse_folder():
    """Abre un cuadro de diálogo para seleccionar una carpeta y devuelve la ruta seleccionada."""
    folder_selected = filedialog.askdirectory()
    return folder_selected

def browse_file():
    """Abre un cuadro de diálogo para seleccionar un archivo de imagen y muestra la imagen seleccionada."""
    file_selected = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if file_selected:
        input_file_var.set(file_selected)
        show_image(file_selected, is_compressed=False)
    return file_selected

def apply_preview():
    """Aplica la compresión y muestra una vista previa de la imagen comprimida."""
    input_path = input_file_var.get()
    if not os.path.isfile(input_path):
        messagebox.showerror("Error", "No se ha seleccionado ninguna imagen para previsualizar.")
        return

    quality = quality_var.get()
    try:
        quality = int(quality)
        if not (1 <= quality <= 100):
            raise ValueError("La calidad debe estar entre 1 y 100.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    resize_factor = resize_var.get()
    try:
        resize_factor = float(resize_factor)
        if resize_factor <= 0:
            raise ValueError("El factor de reducción debe ser positivo.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    convert_to_grayscale = grayscale_var.get()

    quality = validate_quality(quality_var.get()) or 85
    resize_factor = float(resize_factor) if resize_factor else 1.0
    convert_to_grayscale = convert_to_grayscale == 's'

    # Obtener tamaño original de la imagen
    original_size = os.path.getsize(input_path)

    cache_path = compress_and_cache_image(input_path, quality, resize_factor, convert_to_grayscale)
    show_image(cache_path, is_compressed=True, original_size=original_size)

def finalize_compression():
    """Finaliza la compresión y guarda la imagen comprimida en la carpeta de salida especificada."""
    input_path = input_file_var.get()
    output_folder = output_folder_var.get()
    if not validate_output_path(output_folder, CARPETAS_A_VERIFICAR):
        print(f"La ruta de salida debe estar contenida dentro de una de las carpetas permitidas: {', '.join(CARPETAS_A_VERIFICAR)}.")
        messagebox.showerror("Error", "La carpeta de salida no es válida.")
        return
    
    quality = quality_var.get()
    resize_factor = resize_var.get()
    convert_to_grayscale = grayscale_var.get()

    if not os.path.isfile(input_path):
        messagebox.showerror("Error", "No se ha seleccionado ninguna imagen para comprimir.")
        return

    if not validate_folder_path(output_folder):
        messagebox.showerror("Error", "La carpeta de salida no es válida.")
        return

    quality = validate_quality(quality) or 85
    resize_factor = float(resize_factor) if resize_factor else 1.0
    convert_to_grayscale = convert_to_grayscale == 's'

    compressed_path = get_cache_file_path()
    if os.path.exists(compressed_path):
        final_output_path = os.path.join(output_folder, os.path.basename(input_path))
        compress_image(input_path, final_output_path, quality, resize_factor, convert_to_grayscale)
        clear_cache()
        messagebox.showinfo("Finalizado", "Compresión completada y guardada.")
    else:
        messagebox.showerror("Error", "No se encontró la imagen comprimida en caché.")



# Configuración de la Ventana Principal
root = tk.Tk()
root.title("Compresor de Imágenes")



# Variables de Entrada
input_file_var = tk.StringVar()
output_folder_var = tk.StringVar()
quality_var = tk.StringVar(value="85")
resize_var = tk.StringVar(value="1.0")
grayscale_var = tk.StringVar(value="no")



# Widgets de la Interfaz Gráfica
tk.Label(root, text="Seleccionar archivo de imagen:").pack()
tk.Entry(root, textvariable=input_file_var).pack()
tk.Button(root, text="Buscar archivo", command=browse_file).pack()

tk.Label(root, text="Calidad (1-100):").pack()
tk.Entry(root, textvariable=quality_var).pack()

tk.Label(root, text="Factor de reducción (0.1-1.0):").pack()
tk.Entry(root, textvariable=resize_var).pack()

tk.Label(root, text="Convertir a escala de grises (sí/no):").pack()
tk.Entry(root, textvariable=grayscale_var).pack()

tk.Label(root, text="Carpeta de salida:").pack()
tk.Entry(root, textvariable=output_folder_var).pack()
tk.Button(root, text="Buscar carpeta de salida", command=lambda: output_folder_var.set(browse_folder())).pack()

tk.Button(root, text="Aplicar vista previa", command=apply_preview).pack()
tk.Button(root, text="Finalizar compresión", command=finalize_compression).pack()

original_image_label = tk.Label(root)
original_image_label.pack(side=tk.LEFT)

compressed_image_label = tk.Label(root)
compressed_image_label.pack(side=tk.RIGHT)

original_image_info = tk.StringVar()
compressed_image_info = tk.StringVar()

tk.Label(root, textvariable=original_image_info).pack(side=tk.LEFT)
tk.Label(root, textvariable=compressed_image_info).pack(side=tk.RIGHT)

root.mainloop()