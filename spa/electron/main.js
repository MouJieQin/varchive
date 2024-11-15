const { app, BrowserWindow } = require("electron");
const path = require("path");

const NODE_ENV = process.env.NODE_ENV;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  //   mainWindow.loadFile('dist/index.html')
  mainWindow.loadURL(
    NODE_ENV === "development"
      ? "http://localhost:5999"
      : `file://${path.join(__dirname, "../dist/index.html")}`
  );
  if (NODE_ENV === "development") {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") app.quit();
});
