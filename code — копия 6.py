import numpy as np
def compute_sobel_gradients_two_loops(image):
    # Get image dimensions
    height, width = image.shape

    # Initialize output gradients
    gradient_x = np.zeros_like(image, dtype=np.float64)
    gradient_y = np.zeros_like(image, dtype=np.float64)

    # Pad the image with zeros to handle borders
    padded_image = np.pad(image, ((1, 1), (1, 1)), mode='constant', constant_values=0)
# __________end of block__________

    # Define the Sobel kernels for X and Y gradients
    # YOUR CODE HERE
    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    # YOUR CODE HERE
    sobel_y = np.array([[-1, -2, -1], [ 0,  0,  0], [ 1,  2,  1]])

    # Apply Sobel filter for X and Y gradients using convolution
            
    for i in range(1, height + 1):
        for j in range(1, width + 1):
            # YOUR CODE HERE
            region = padded_image[i-1:i+2, j-1:j+2]
            gradient_x[i-1, j-1] = np.sum(region * sobel_x)
            gradient_y[i-1, j-1] = np.sum(region * sobel_y)

    return gradient_x, gradient_y

import numpy as np # for your convenience when you copy the code to the contest
def compute_gradient_magnitude(sobel_x, sobel_y):
    '''
    Compute the magnitude of the gradient given the x and y gradients.

    Inputs:
        sobel_x: numpy array of the x gradient.
        sobel_y: numpy array of the y gradient.

    Returns:
        magnitude: numpy array of the same shape as the input [0] with the magnitude of the gradient.
    '''
    
    # YOUR CODE HERE
    return np.sqrt(sobel_x**2 + sobel_y**2)


def compute_gradient_direction(sobel_x, sobel_y):
    '''
    Compute the direction of the gradient given the x and y gradients. Angle must be in degrees in the range (-180; 180].
    Use arctan2 function to compute the angle.

    Inputs:
        sobel_x: numpy array of the x gradient.
        sobel_y: numpy array of the y gradient.

    Returns:
        gradient_direction: numpy array of the same shape as the input [0] with the direction of the gradient.
    '''
    # YOUR CODE HERE
    return np.arctan2(sobel_y, sobel_x)

cell_size = 7
def compute_hog(image, pixels_per_cell=(cell_size, cell_size), bins=9):
    # 1. Convert the image to grayscale if it's not already (assuming the image is in RGB or BGR)
    if len(image.shape) == 3:
        image = np.mean(image, axis=2)  # Simple averaging to convert to grayscale
    
    # 2. Compute gradients with Sobel filter
    gradient_x, gradient_y = compute_sobel_gradients_two_loops(image)

    # 3. Compute gradient magnitude and direction
    magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    direction = np.arctan2(gradient_y, gradient_x) * 180 / np.pi

    # 4. Create histograms of gradient directions for each cell
    cell_height, cell_width = pixels_per_cell
    n_cells_x = image.shape[1] // cell_width
    n_cells_y = image.shape[0] // cell_height

    histograms = np.zeros((n_cells_y, n_cells_x, bins))
    
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            # Определяем пиксели для центральной ячейки
            cell_magnitude = magnitude[y * cell_height : (y + 1) * cell_height, x * cell_width : (x + 1) * cell_width]
            cell_direction = direction[y * cell_height : (y + 1) * cell_height, x * cell_width : (x + 1) * cell_width]
            
            # Для каждой ячейки вычисляем гистограмму направлений
            hist, bin_edges = np.histogram(cell_direction, bins=bins, range=(-180, 180), weights=cell_magnitude, density=False)
            
            # Зануляем бин для 180 градусов, если он существует
            bin_center = (bin_edges[:-1] + bin_edges[1:]) / 2  # Находим центры бинов
            if 180 in bin_center:
                bin_index_180 = np.where(bin_center == 180)[0][0]
                hist[bin_index_180] = 0  # Зануляем бин для 180°

            # Нормализуем гистограмму так, чтобы сумма всех бинов была равна 1
            hist_sum = np.sum(hist)
            if hist_sum != 0:
                hist = hist / hist_sum  # Нормализуем значения гистограммы

            # Сохраняем гистограмму для центра ячейки
            histograms[y, x] = hist

    return histograms
