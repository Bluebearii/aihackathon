document.addEventListener('DOMContentLoaded', () => {
    // --- Tab Switching Logic ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active class from all nav items and tabs
            navItems.forEach(nav => nav.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));

            // Add active class to clicked nav item
            item.classList.add('active');
            
            // Show corresponding tab content
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // --- Toast Notification ---
    const showToast = (message) => {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    };

    // --- Data Fetching and Rendering ---

    // 1. Schedule Optimizer
    fetch('/api/schedule')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#schedule-table tbody');
            data.forEach(apt => {
                const tr = document.createElement('tr');
                
                // Determine action button
                let actionBtn = '';
                if (apt.risk_level === 'High') {
                    if (apt.neighborhood === 'JARDIM DA PENHA' || apt.neighborhood === 'JARDIM CAMBURI') {
                        actionBtn = `<button class="action-btn" onclick="window.showToast('Uber Health Voucher Sent to ${apt.patient}')">Send Uber Health</button>`;
                    } else {
                        actionBtn = `<button class="action-btn" onclick="window.showToast('Slot Double Booked for ${apt.time}')">Double Book</button>`;
                    }
                } else if (apt.risk_level === 'Medium') {
                    actionBtn = `<button class="action-btn" onclick="window.showToast('Telehealth Link Sent to ${apt.patient}')">Offer Telehealth</button>`;
                } else {
                    actionBtn = `<span style="color: #8D99AE; font-size: 0.85rem;">No Action Needed</span>`;
                }

                tr.innerHTML = `
                    <td>${apt.time}</td>
                    <td><strong>${apt.patient}</strong><br><span style="font-size: 0.8rem; color: #8D99AE;">Age: ${apt.age}</span></td>
                    <td>${apt.condition}</td>
                    <td>${apt.wait_days} Days</td>
                    <td><span class="badge ${apt.risk_level.toLowerCase()}">${apt.risk_score}% (${apt.risk_level})</span></td>
                    <td>${actionBtn}</td>
                `;
                tbody.appendChild(tr);
            });
        });

    // 2. Pricing Auditor
    fetch('/api/pricing')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#pricing-table tbody');
            data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.state}</strong></td>
                    <td>${item.procedure}</td>
                    <td>$${item.avg_charge.toLocaleString()}</td>
                    <td>$${item.medicare_payment.toLocaleString()}</td>
                    <td><span style="color: #E76F51; font-weight: 500;">${item.write_off_pct}%</span></td>
                    <td><span class="badge ${item.status === 'Critical' ? 'high' : 'medium'}">${item.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        });

    // 3. OOP Estimator
    fetch('/api/insurance')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#oop-table tbody');
            data.forEach(item => {
                const tr = document.createElement('tr');
                
                let actionBtn = item.risk.includes('High') 
                    ? `<button class="action-btn" onclick="window.showToast('Financial Assistance Offered to ${item.name}')">Offer Assistance</button>`
                    : `<span style="color: #8D99AE; font-size: 0.85rem;">Standard Billing</span>`;

                tr.innerHTML = `
                    <td><strong>${item.name}</strong><br><span style="font-size: 0.8rem; color: #8D99AE;">${item.patient_id}</span></td>
                    <td>${item.procedure}</td>
                    <td>${item.insurance}</td>
                    <td>$${item.estimated_cost.toLocaleString()}</td>
                    <td><span style="font-weight: 600; color: ${item.patient_oop > 1000 ? '#E76F51' : '#2A9D8F'};">$${item.patient_oop.toLocaleString()}</span></td>
                    <td>${actionBtn}</td>
                `;
                tbody.appendChild(tr);
            });
        });

    // Expose showToast globally for inline onclick handlers
    window.showToast = showToast;
});
