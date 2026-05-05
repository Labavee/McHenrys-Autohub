document.addEventListener('DOMContentLoaded', () => {
    requireAuthentication();
    loadInvoices();
});

async function loadInvoices() {
    const invoices = await apiCall('GET', '/invoices');
    displayInvoices(invoices);
}

function displayInvoices(invoices) {
    const tbody = document.getElementById('invoicesBody');
    
    if (!invoices || invoices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading">No invoices found</td></tr>';
        return;
    }
    
    tbody.innerHTML = invoices.map(invoice => `
        <tr>
            <td>${invoice.invoice_number}</td>
            <td>${new Date(invoice.invoice_date).toLocaleDateString()}</td>
            <td>${invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : 'N/A'}</td>
            <td>$${invoice.total.toFixed(2)}</td>
            <td><span class="status-badge status-${invoice.status}">${invoice.status}</span></td>
            <td>
                <button class="btn btn-secondary" onclick="viewInvoiceDetails(${invoice.id})">View</button>
            </td>
        </tr>
    `).join('');
}

async function viewInvoiceDetails(invoiceId) {
    const invoice = await apiCall('GET', `/invoices/${invoiceId}`);
    
    if (invoice.id) {
        const details = `
Invoice Number: ${invoice.invoice_number}
Customer ID: ${invoice.customer_id}
Issue Date: ${new Date(invoice.invoice_date).toLocaleDateString()}
Due Date: ${invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : 'N/A'}
Subtotal: $${invoice.subtotal}
Tax: $${invoice.tax}
Total: $${invoice.total}
Status: ${invoice.status}

Items:
${invoice.items.map(item => `- ${item.description}: ${item.quantity} x $${item.unit_price} = $${item.total_price}`).join('\n')}
        `;
        alert(details);
    }
}
