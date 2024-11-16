const { app, BrowserWindow } = require("electron");
const path = require("path");
const { exec } = require("child_process");
const { dialog } = require("electron");

const splits = __dirname.split("/");
const varchivePath = splits.splice(0, splits.length - 2).join("/");

const startPath = varchivePath.concat("/shell/varchive-start");

function runShellCommand(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject({ error, stderr });
      } else {
        resolve(stdout);
      }
    });
  });
}

async function startServer() {
  await runShellCommand(startPath)
    .then((stdout) => {
      console.log("Output:", stdout);
      // Continue your code here
    })
    .catch(({ error, stderr }) => {
      const options = {
        type: "error",
        title: "Error",
        message: `${startPath},${stderr}`,
        buttons: ["OK"],
      };
      dialog.showMessageBox(options);
      return;
    });
}

const NODE_ENV = process.env.NODE_ENV;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  mainWindow.loadURL(
    NODE_ENV === "development"
      ? "http://localhost:5999/"
      : "http://localhost:5999/"
    // : `file://${path.join(__dirname, "../dist/index.html")}`
  );
  if (NODE_ENV === "development") {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(async () => {
  await startServer();
  createWindow();
  app.on("activate", function () {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", function () {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
