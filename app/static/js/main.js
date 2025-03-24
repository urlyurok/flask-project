// main.js

// Функция для загрузки всех продуктов
function loadProducts() {
    fetch('/api/products')  // Запрос к API для получения списка продуктов
        .then(response => response.json())  // Преобразуем ответ в JSON
        .then(data => {
            // Выводим список продуктов на страницу
            const productsContainer = document.getElementById('products-container');
            productsContainer.innerHTML = '';  // Очищаем контейнер перед заполнением
            data.forEach(product => {
                const productElement = document.createElement('div');
                productElement.classList.add('product');
                productElement.innerHTML = `
                    <h3>${product.name}</h3>
                    <p>Категория: ${product.category.name}</p>
                    <p>Цена: ${product.price}</p>
                `;
                productsContainer.appendChild(productElement);
            });
        })
        .catch(error => console.error('Error loading products:', error));  // Обрабатываем ошибки
}

// Функция для загрузки аналитики по продажам
function loadSalesAnalytics() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    fetch(`/api/sales/total?start_date=${startDate}&end_date=${endDate}`)  // Запрос к API для общей суммы продаж
        .then(response => response.json())
        .then(data => {
            const totalSalesContainer = document.getElementById('total-sales');
            totalSalesContainer.innerHTML = `Total Sales: ${data.total_sales}`;
        })
        .catch(error => console.error('Error loading sales analytics:', error));  // Обрабатываем ошибки
}

// Функция для загрузки топ-N самых продаваемых товаров
function loadTopProducts() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const limit = document.getElementById('limit').value;

    fetch(`/api/sales/top-products?start_date=${startDate}&end_date=${endDate}&limit=${limit}`)  // Запрос к API для топ-N продуктов
        .then(response => response.json())
        .then(data => {
            const topProductsContainer = document.getElementById('top-products-container');
            topProductsContainer.innerHTML = '';  // Очищаем контейнер перед заполнением
            data.forEach(product => {
                const productElement = document.createElement('div');
                productElement.classList.add('top-product');
                productElement.innerHTML = `
                    <h3>${product.name}</h3>
                    <p>Продано: ${product.sales}</p>
                `;
                topProductsContainer.appendChild(productElement);
            });
        })
        .catch(error => console.error('Error loading top products:', error));  // Обрабатываем ошибки
}

// Добавляем обработчики событий для кнопок
document.addEventListener('DOMContentLoaded', function () {
    loadProducts();  // Загружаем продукты при загрузке страницы

    // Обработчики для аналитики
    const salesButton = document.getElementById('sales-button');
    if (salesButton) {
        salesButton.addEventListener('click', loadSalesAnalytics);
    }

    // Обработчик для загрузки топ-N продуктов
    const topProductsButton = document.getElementById('top-products-button');
    if (topProductsButton) {
        topProductsButton.addEventListener('click', loadTopProducts);
    }
});
