const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to React renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  isDesktopApp: true,
  getVersion: () => ipcRenderer.invoke('app:get-version'),
  listScannerDevices: () => ipcRenderer.invoke('scanner:list-devices'),
  scanFromDevice: (options) => ipcRenderer.invoke('scanner:scan-page', options),
});
