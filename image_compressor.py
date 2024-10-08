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
            img.thumbnail((200, 200))  # Redimensionar la imagen para que quepa en el Label
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



def toggle_entry_fields():
    # Alterna entre habilitar y deshabilitar
    state = tk.NORMAL if entry_fields_disabled.get() else tk.DISABLED

    # Configura el estado de los campos de entrada
    for widget in [input_file_entry, output_folder_entry, quality_entry, resize_entry, grayscale_entry]:
        widget.config(state=state)

    # Configura el estado de los botones
    for widget in [browse_button, folder_button, compress_button]:
        widget.config(state=state)
    
    # Alterna el estado de la variable de control
    entry_fields_disabled.set(not entry_fields_disabled.get())

def find_optimal_compression():
    """Encuentra la configuración óptima para comprimir la imagen al tamaño deseado."""
    input_path = input_file_var.get()
    if not os.path.isfile(input_path):
        messagebox.showerror("Error", "No se ha seleccionado ninguna imagen para comprimir.")
        return

    try:
        max_weight_kb = float(max_weight_var.get())
        if max_weight_kb <= 0:
            raise ValueError("El peso máximo debe ser un número positivo.")
        min_weight_kb = max_weight_kb * 0.8  # Se acepta hasta el 80% del peso máximo deseado como mínimo
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return
    
    max_attempts = int(attempts_var.get())
    initial_quality = 100
    min_quality = 20
    initial_resize_factor = 1.0
    min_resize_factor = 0.1
    quality_decrement = 20
    resize_decrement = 0.1
    
    best_quality = None
    best_resize_factor = None
    best_file_size = float('inf')
    best_compression = None

    attempts = 0

    # Primera fase: Reducción de calidad manteniendo el factor de redimensionamiento en 1.0
    quality = initial_quality
    resize_factor = initial_resize_factor

    while attempts < max_attempts and quality >= min_quality:
        cache_path = compress_and_cache_image(input_path, quality, resize_factor, False)
        file_size = os.path.getsize(cache_path) / 1024  # Tamaño en KB

        if min_weight_kb <= file_size <= max_weight_kb and file_size < best_file_size:
            best_file_size = file_size
            best_quality = quality
            best_resize_factor = resize_factor
            best_compression = cache_path

        attempts += 1
        quality -= quality_decrement

    # Segunda fase: Reducción del factor de redimensionamiento con la calidad mínima alcanzada
    quality = min_quality
    while attempts < max_attempts and resize_factor >= min_resize_factor:
        cache_path = compress_and_cache_image(input_path, quality, resize_factor, False)
        file_size = os.path.getsize(cache_path) / 1024  # Tamaño en KB

        if min_weight_kb <= file_size <= max_weight_kb and file_size < best_file_size:
            best_file_size = file_size
            best_quality = quality
            best_resize_factor = resize_factor
            best_compression = cache_path

        attempts += 1
        resize_factor -= resize_decrement
        print(max_attempts, attempts, resize_factor, min_resize_factor)

    if best_compression:
        messagebox.showinfo("Óptimo Encontrado",
            f"La mejor configuración encontrada:\n"
            f"Calidad: {best_quality}\n"
            f"Factor de Reducción: {best_resize_factor}\n"
            f"Tamaño: {best_file_size:.2f} KB")
        
        quality_var.set(value=best_quality)
        resize_var.set(value=best_resize_factor)
        apply_preview()
    else:
        messagebox.showinfo("Óptimo Encontrado", "No se encontró una configuración que cumpla con el peso deseado.")




# Configuración de la Ventana Principal
root = tk.Tk()
root.title("Compresor de Imágenes")

# Variables de Entrada
input_file_var = tk.StringVar()
output_folder_var = tk.StringVar()
quality_var = tk.StringVar(value="85")
resize_var = tk.StringVar(value="1.0")
grayscale_var = tk.StringVar(value="n")
entry_fields_disabled = tk.BooleanVar(value=False)
max_weight_var = tk.StringVar(value="100")  # Peso máximo en KB

# Layout de la GUI
tk.Label(root, text="CONFIGURACIONES:").grid(row=0, column=0, padx=10, pady=5)
tk.Label(root, text="-----------------------------------------------------").grid(row=0, column=1, padx=10, pady=5)
tk.Label(root, text="----------------").grid(row=0, column=2, padx=10, pady=5)
tk.Label(root, text="|").grid(row=0, column=3, padx=10, pady=5)
tk.Label(root, text="ACCIONES:").grid(row=0, column=4, padx=10, pady=5)


tk.Label(root, text="Seleccionar Imagen:").grid(row=1, column=0, padx=10, pady=5)
input_file_entry = tk.Entry(root, textvariable=input_file_var, width=50)
input_file_entry.grid(row=1, column=1, padx=10, pady=5)
browse_button = tk.Button(root, text="Buscar", command=browse_file)
browse_button.grid(row=1, column=2, padx=10, pady=5)
tk.Label(root, text="|").grid(row=1, column=3, padx=10, pady=5)
preview_button = tk.Button(root, text="Previsualizar", command=apply_preview)
preview_button.grid(row=1, column=4, pady=10)


tk.Label(root, text="Carpeta de Salida:").grid(row=2, column=0, padx=10, pady=5)
output_folder_entry = tk.Entry(root, textvariable=output_folder_var, width=50)
output_folder_entry.grid(row=2, column=1, padx=10, pady=5)
folder_button = tk.Button(root, text="Buscar Carpeta", command=lambda: output_folder_var.set(browse_folder()))
folder_button.grid(row=2, column=2, padx=10, pady=5)
tk.Label(root, text="|").grid(row=2, column=3, padx=10, pady=5)
compress_button = tk.Button(root, text="Comprimir y Guardar", command=finalize_compression)
compress_button.grid(row=2, column=4, pady=10)


tk.Label(root, text="Calidad (1 - 100):").grid(row=3, column=0, padx=10, pady=5)
quality_entry = tk.Entry(root, textvariable=quality_var, width=10)
quality_entry.grid(row=3, column=1, padx=10, pady=5)
tk.Label(root, text="|").grid(row=3, column=3, padx=10, pady=5)
tk.Button(root, text="Busqueda Automática", command=find_optimal_compression).grid(row=3, column=4, columnspan=3, padx=10, pady=5)


tk.Label(root, text="Factor de Reducción (0.1 - 1.0):").grid(row=4, column=0, padx=10, pady=5)
resize_entry = tk.Entry(root, textvariable=resize_var, width=10)
resize_entry.grid(row=4, column=1, padx=10, pady=5)
tk.Label(root, text="|").grid(row=4, column=3, padx=10, pady=5)


tk.Label(root, text="Grayscale (s/n):").grid(row=5, column=0, padx=10, pady=5)
grayscale_entry = tk.Entry(root, textvariable=grayscale_var, width=10)
grayscale_entry.grid(row=5, column=1, padx=10, pady=5)
tk.Label(root, text="|").grid(row=5, column=3, padx=10, pady=5)


tk.Label(root, text="Peso Máximo (KB)").grid(row=6, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=max_weight_var, width=10).grid(row=6, column=1, padx=10, pady=5)

# Agregar campo para el número máximo de intentos
attempts_label = tk.Label(root, text="Número máximo de intentos:").grid(row=6, column=2, padx=10, pady=5)
attempts_var = tk.StringVar(value='10')
attempts_entry = tk.Entry(root, textvariable=attempts_var, width=10).grid(row=6, column=4, padx=10, pady=5)


# Imágenes y etiquetas para la visualización
original_image_label = tk.Label(root)
original_image_label.grid(row=7, column=0, pady=10)


compressed_image_label = tk.Label(root)
compressed_image_label.grid(row=7, column=1, pady=10)


original_image_info = tk.StringVar()
compressed_image_info = tk.StringVar()


tk.Label(root, textvariable=original_image_info).grid(row=8, column=0,  pady=5)
tk.Label(root, textvariable=compressed_image_info).grid(row=8, column=1,  pady=5)


# Botón para habilitar/deshabilitar campos
toggle_button = tk.Button(root, text="Habilitar/Deshabilitar Campos", command=toggle_entry_fields)
toggle_button.grid(row=9, column=0, columnspan=4, pady=10)



# Crear la carpeta de caché al iniciar
create_cache_folder()


root.mainloop()