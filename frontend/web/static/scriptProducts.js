function getProducts() {
    fetch('http://192.168.80.4:5003/api/products', {
     method: 'GET',
     headers: {
        'Content-Type': 'application/json'
        },
     credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            // Handle data
            console.log(data);

            // Get table body
            var productListBody = document.querySelector('#product-list tbody');
            productListBody.innerHTML = ''; // Clear previous data

            // Loop through products and populate table rows
            data.forEach(product => {
                var row = document.createElement('tr');

                // Id
                var idCell = document.createElement('td');
                idCell.textContent = product.id;
                row.appendChild(idCell);

                // Name
                var nameCell = document.createElement('td');
                nameCell.textContent = product.name;
                row.appendChild(nameCell);

                    // Price
                    var priceCell = document.createElement('td');
                    priceCell.textContent = product.priceU;
                    row.appendChild(priceCell);

                // Quantity
                var quantityCell = document.createElement('td');
                quantityCell.textContent = product.quantity;
                row.appendChild(quantityCell);

		// Order
		var orderInput = document.createElement('input');
		orderInput.type = 'text';
		orderInput.value = "0";
		row.appendChild(orderInput);

                // Actions
                var actionsCell = document.createElement('td');

                // Edit link
                var editLink = document.createElement('a');
                editLink.href = `/editProduct/${product.id}`;
                //editLink.href = `edit.html?id=${product.id}`;
                editLink.textContent = 'Edit';
                editLink.className = 'btn btn-primary mr-2';
                actionsCell.appendChild(editLink);

                // Delete link
                var deleteLink = document.createElement('a');
                deleteLink.href = '#';
                deleteLink.textContent = 'Delete';
                deleteLink.className = 'btn btn-danger';
                deleteLink.addEventListener('click', function() {
                    deleteProduct(product.id);
                });
                actionsCell.appendChild(deleteLink);

                row.appendChild(actionsCell);

                productListBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error:', error));
}

function createProduct() {
    var nameVal = document.getElementById('name').value;
    var quantityVal = parseInt(document.getElementById('quantity').value, 10);
    var priceVal = parseFloat(document.getElementById('price').value);

    var data = {
        name: nameVal,
        quantity: isNaN(quantityVal) ? 0 : quantityVal,
        priceU: isNaN(priceVal) ? 0.0 : priceVal
    };

    fetch('http://192.168.80.4:5003/api/products', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle success
        console.log(data);
    })
    .catch(error => {
        // Handle error
        console.error('Error:', error);
    });
}

function updateProduct() {

    //const userName = '{{ username }}';
    //console.log('userName: ',userName);

    var productId = document.getElementById('product-id').value;
    var nameVal = document.getElementById('name').value;
    var quantityVal = parseInt(document.getElementById('quantity').value, 10);
    var priceVal = parseFloat(document.getElementById('price').value);

    var data = {
        name: nameVal,
        quantity: isNaN(quantityVal) ? 0 : quantityVal,
        priceU: isNaN(priceVal) ? 0.0 : priceVal
    };

    fetch(`http://192.168.80.4:5003/api/products/${productId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Handle success
        console.log(data);
        // Optionally, redirect to another page or show a success message
    })
    .catch(error => {
        // Handle error
        console.error('Error:', error);
    });
}



function deleteProduct(productId) {
    console.log('Deleting product with ID:', productId);
    if (confirm('Are you sure you want to delete this product?')) {
        fetch(`http://192.168.80.4:5003/api/products/${productId}`, {
            method: 'DELETE',
            credentials: 'include'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Handle success
            console.log('Product deleted successfully:', data);
            // Reload the product list
            getProducts();
        })
        .catch(error => {
            // Handle error
            console.error('Error:', error);
        });
    }
}


function orderProducts() {
  // Obtener los productos seleccionados y sus cantidades
  const selectedProducts = [];
  const productRows = document.querySelectorAll('#product-list tbody tr');
  productRows.forEach(row => {
    const quantityInput = row.querySelector('input[type="text"]');
    const quantity = parseInt(quantityInput.value);
    if (quantity > 0) {
      //const productId = row.id.split('-')[1]; // Extraer el ID del producto del atributo id de la fila
	    //
      var productId = row.querySelector('td:nth-child(1)').textContent;
      //const productId = row.id.textContent; // Extraer el ID del producto del atributo id de la fila
      selectedProducts.push({ id: productId, quantity });
    }
  });

  // Si no hay productos seleccionados, mostrar un mensaje de error
  if (selectedProducts.length === 0) {
    alert('Por favor, selecciona al menos un producto para realizar la orden.');
    return;
  }

  // Preparar los datos de la orden
  const orderData = {
    user: {
      name: sessionStorage.getItem('username'),
      email: sessionStorage.getItem('email')
    },
    products: selectedProducts
  };

  // Enviar los datos de la orden al endpoint
  fetch('http://192.168.80.4:5004/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orderData),
    credentials: 'include'
  })
  .then(response => response.json())
  .then(data => {
    if (data.message === 'Orden creada exitosamente') {
      console.log('Orden creada exitosamente!');
      // Mostrar un mensaje de confirmación al usuario
      alert('¡Orden creada exitosamente!');
      // Actualizar la interfaz de usuario para reflejar los cambios (opcional)
    } else {
      console.error('Error al crear la orden:', data.message);
      // Mostrar un mensaje de error al usuario
      alert('Error al crear la orden. Por favor, intenta nuevamente.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Ocurrió un error al procesar la orden. Por favor, intenta nuevamente.');
  });
}


/* Orders management functions */
function getOrders() {
    fetch('http://192.168.80.4:5004/api/orders', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Orders:', data);
        var orderListBody = document.querySelector('#order-list tbody');
        if (!orderListBody) return;
        orderListBody.innerHTML = '';
        data.forEach(order => {
            var row = document.createElement('tr');

            var idCell = document.createElement('td');
            idCell.textContent = order.id;
            row.appendChild(idCell);

            var userCell = document.createElement('td');
            userCell.textContent = order.user && order.user.name ? order.user.name : '';
            row.appendChild(userCell);

            var emailCell = document.createElement('td');
            emailCell.textContent = order.user && order.user.email ? order.user.email : '';
            row.appendChild(emailCell);

            var productsCell = document.createElement('td');
            if (Array.isArray(order.products)) {
                // Prefer product name when available, otherwise fall back to id
                productsCell.innerHTML = '<ul class="mb-0">' + order.products.map(p => {
                    const name = p.name || p.product_name || p.productId || p.id || p.product_id || 'unknown';
                    const qty = p.quantity || p.qty || 0;
                    return `<li>${name}: ${qty}</li>`;
                }).join('') + '</ul>';
            } else {
                productsCell.textContent = '';
            }
            row.appendChild(productsCell);

            var totalCell = document.createElement('td');
            totalCell.textContent = typeof order.total !== 'undefined' ? Number(order.total).toFixed(2) : '';
            row.appendChild(totalCell);

            var createdCell = document.createElement('td');
            createdCell.textContent = order.created_at ? new Date(order.created_at).toLocaleString() : '';
            row.appendChild(createdCell);

            var actionsCell = document.createElement('td');
            var viewLink = document.createElement('a');
            viewLink.href = '#';
            viewLink.textContent = 'View';
            viewLink.className = 'btn btn-secondary mr-2';
            viewLink.addEventListener('click', function(e) { e.preventDefault(); getOrder(order.id); });
            actionsCell.appendChild(viewLink);

            var deleteLink = document.createElement('a');
            deleteLink.href = '#';
            deleteLink.textContent = 'Delete';
            deleteLink.className = 'btn btn-danger';
            deleteLink.addEventListener('click', function(e) { e.preventDefault(); deleteOrder(order.id); });
            actionsCell.appendChild(deleteLink);

            row.appendChild(actionsCell);
            orderListBody.appendChild(row);
        });
    })
    .catch(error => console.error('Error fetching orders:', error));
}

function getOrder(orderId) {
    fetch(`http://192.168.80.4:5004/api/orders/${orderId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('Order details:', data);
        alert(JSON.stringify(data, null, 2));
    })
    .catch(error => console.error('Error getting order:', error));
}

function deleteOrder(orderId) {
    if (!confirm('Are you sure you want to delete this order?')) return;
    fetch(`http://192.168.80.4:5004/api/orders/${orderId}`, {
        method: 'DELETE',
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        console.log('Order deleted:', data);
        getOrders();
    })
    .catch(error => console.error('Error deleting order:', error));
}
