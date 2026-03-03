const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    platform: process.platform,
    versions: process.versions,
    // Add any necessary IPC bridges here
});
