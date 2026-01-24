<script>
const logs = [
{ accion: 'Conexión', usuario: 'admin', fecha: '2025-12-18 21:45:12' },
{ accion: 'Desconexión', usuario: 'admin', fecha: '2025-12-18 22:10:03' },
{ accion: 'Conexión', usuario: 'soporte', fecha: '2025-12-18 22:30:41' },
];


const tbody = document.querySelector('tbody');
const indicator = document.querySelector('.indicator');
const statusText = document.querySelector('.status-text');


function renderLogs() {
tbody.innerHTML = '';
logs.forEach(log => {
const tr = document.createElement('tr');
tr.classList.add('log');
tr.classList.add(log.accion === 'Conexión' ? 'connect' : 'disconnect');


tr.innerHTML = `
<td>${log.accion}</td>
<td>${log.usuario}</td>
<td>${log.fecha}</td>
`;


tbody.appendChild(tr);
});
}


function updateStatus() {
const lastLog = logs[logs.length - 1];
if (lastLog.accion === 'Conexión') {
indicator.classList.add('online');
statusText.textContent = 'Base de datos conectada';
} else {
indicator.classList.remove('online');
statusText.textContent = 'Base de datos desconectada';
}
}


// Simula nuevas conexiones/desconexiones cada 5 segundos
setInterval(() => {
const accion = Math.random() > 0.5 ? 'Conexión' : 'Desconexión';
const now = new Date().toISOString().replace('T', ' ').substring(0, 19);


logs.push({
accion,
usuario: 'sistema',
fecha: now
});


renderLogs();
updateStatus();
}, 5000);


// Render inicial
renderLogs();
updateStatus();
</script>