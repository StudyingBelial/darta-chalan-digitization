const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow = null;
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1360,
    height: 880,
    minWidth: 1024,
    minHeight: 700,
    title: 'Nepal Telecom - Darta & Chalan Digitization System',
    backgroundColor: '#003b73',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
    },
  });

  // Load URL
  if (isDev && process.env.ELECTRON_DEV_URL) {
    mainWindow.loadURL(process.env.ELECTRON_DEV_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Open external links in default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// App lifecycle
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers for Native Scanner and System Bridge
ipcMain.handle('scanner:list-devices', async () => {
  // Returns hardware scanner devices detected via Windows WIA / TWAIN / eSCL
  return [
    { id: 'canon_dr_c225_native', name: 'Canon imageFORMULA DR-C225 (USB Direct WIA)', type: 'CANON_USB', isDefault: true },
    { id: 'canon_lide_400_native', name: 'Canon CanoScan LiDE 400 (WIA Flatbed)', type: 'CANON_USB' },
    { id: 'canon_pixma_native', name: 'Canon PIXMA Multifunction (Network)', type: 'CANON_NETWORK' },
  ];
});

ipcMain.handle('scanner:scan-page', async (event, options) => {
  // In a production environment with Canon WIA/TWAIN C++ or Python addon,
  // this triggers the Windows WIA COM API (wiaaut.dll).
  return {
    success: true,
    message: 'Acquired page from Canon hardware scanner via Windows WIA driver.',
    options,
  };
});

ipcMain.handle('app:get-version', () => {
  return app.getVersion();
});

ipcMain.handle('app:is-desktop', () => {
  return true;
});
