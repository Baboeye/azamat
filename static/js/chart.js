document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Добавляем таймер на скрытие
        setTimeout(() => {
            // Плавное исчезновение
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            
            // Удаляем из DOM после анимации
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 4000);
    });
    
    // Добавляем кнопку закрытия для каждого алерта
    alerts.forEach(alert => {
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '✕';
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: inherit;
            cursor: pointer;
            font-size: 18px;
            margin-left: 12px;
            padding: 0;
            opacity: 0.6;
        `;
        closeBtn.onmouseover = () => closeBtn.style.opacity = '1';
        closeBtn.onmouseout = () => closeBtn.style.opacity = '0.6';
        closeBtn.onclick = () => {
            alert.style.transition = 'all 0.3s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 300);
        };
        
        alert.appendChild(closeBtn);
    });
});