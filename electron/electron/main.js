const { app, BrowserWindow, screen } = require("electron");
const path = require("path");
const { exec } = require("child_process");
const { dialog } = require("electron");

const splits = __dirname.split("/");
const varchivePath = splits.splice(0, splits.length - 2).join("/");

const checkInstallPath = varchivePath.concat("/shell/varchive-checkInstall");
const installPath = varchivePath.concat("/install");
const startPath = varchivePath.concat("/shell/varchive-start");
const stopPath = varchivePath.concat("/shell/varchive-stop");

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

async function install() {
    const installCmd = "open ".concat(
        installPath,
        " && sleep 3 && ",
        checkInstallPath,
        " closed"
    );
    console.log("installCmd:", installCmd);
    return await runShellCommand(installCmd)
        .then((stdout) => {
            console.log("Output:", stdout);
            return 0;
        })
        .catch(async ({ error, stderr }) => {
            const options = {
                type: "error",
                message: `${installPath}`,
                detail: `${stderr}`,
                buttons: ["OK"],
            };
            await dialog.showMessageBox(options);
            return 1;
        });
}

async function checkInstall() {
    return await runShellCommand(checkInstallPath)
        .then((stdout) => {
            return 0;
        })
        .catch(async ({ error, stderr }) => {
            const options = {
                type: "info",
                message:
                    "You will be asked to input your system password into a terminal app installing dependences.",
                detail: `${stderr}`,
                buttons: ["Exit", "Install"],
            };
            const responses = await dialog.showMessageBox(options);
            if (responses.response === 0) {
                // Exit button pressed
                return -1;
            } else if (responses.response === 1) {
                // Install button pressed
                await install();
                return await checkInstall();
            }
            return -2;
        });
}

async function startServer() {
    await runShellCommand(startPath)
        .then((stdout) => {
            console.log("Output:", `${stdout}`);
            return;
        })
        .catch(async ({ error, stderr }) => {
            const options = {
                type: "error",
                message: `${startPath}`,
                detail: `${stderr}`,
                buttons: ["OK"],
            };
            await dialog.showMessageBox(options);
            return;
        });
}

const NODE_ENV = process.env.NODE_ENV;

function createWindow() {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    const mainWindow = new BrowserWindow({
        width: width,
        height: height,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
        },
    });

    mainWindow.loadURL("http://localhost:5999/");
    if (NODE_ENV === "development") {
        mainWindow.webContents.openDevTools();
    }
}

app.whenReady().then(async () => {
    const res = await checkInstall();
    if (res !== 0) {
        app.quit();
    } else {
        await startServer();
        createWindow();
        app.on("activate", function () {
            if (BrowserWindow.getAllWindows().length === 0) {
                createWindow();
            }
        });
    }
});

app.on("window-all-closed", function () {
    if (process.platform !== "darwin") {
        app.quit();
    }
});
