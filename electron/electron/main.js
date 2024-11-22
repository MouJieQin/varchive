const { app, BrowserWindow, screen, Menu, MenuItem } = require("electron");
const path = require("path");
const { exec } = require("child_process");
const { dialog } = require("electron");

const splits = __dirname.split("/");
const varchivePath = splits.splice(0, splits.length - 2).join("/");

const checkInstallPath = varchivePath.concat("/shell/varchive-checkInstall");
const installPath = varchivePath.concat("/install");
const startPath = varchivePath.concat("/shell/varchive-start");

// Create the dock menu template
const dockMenuTemplate = [
    {
        label: "File",
        submenu: [
            {
                label: "Custom",
                click() {
                    // Action to perform when the menu item is clicked
                    console.log("Custom option clicked");
                },
            },
            { type: "separator" },
            { role: "quit" },
        ],
    },
];
// Build the dock menu from the template
const dockMenu = Menu.buildFromTemplate(dockMenuTemplate);
// Set the application dock menu
app.dock.setMenu(dockMenu);

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

async function curl(path, jsonStr) {
    const url = "https://127.0.0.1:8999".concat(path);
    const curlCmd = "".concat(
        "curl -X POST ",
        url,
        ' -H "Content-Type: application/json" -d ',
        "'",
        jsonStr,
        "'"
    );
    console.log("curlCmd:", curlCmd);
    return await runShellCommand(curlCmd)
        .then((stdout) => {
            console.log("curl: ", stdout);
            return {
                returnCode: 0,
                stdout: stdout,
            };
            return stdout;
        })
        .catch(async ({ error, stderr }) => {
            const options = {
                type: "error",
                message: `${installPath}`,
                detail: `${stderr}`,
                buttons: ["OK"],
            };
            await dialog.showMessageBox(options);
            return { returnCode: 1 };
        });
}

async function serverOperate(command) {
    const response = await curl(
        "/varchive/server/",
        JSON.stringify({
            command: command,
        })
    );
    return response;
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

async function handleShutdown() {
    const res = await serverOperate(["shutdown", "default"]);
}

async function cancelShutdown() {
    const res = await serverOperate(["shutdown", "cancel"]);
}

function setDockMenu() {
    // Get the existing menu items
    const dockMenu = app.dock.getMenu();
    // Add a new option to the dock menu
    dockMenu.append(
        new MenuItem({
            label: "Open a new Window",
            click() {
                createWindow();
                // Action to be performed when the new menu item is clicked
            },
        })
    );

    // Set the updated dock menu
    app.dock.setMenu(dockMenu);
}

app.whenReady().then(async () => {
    setDockMenu();
    const res = await checkInstall();
    if (res !== 0) {
        app.quit();
    } else {
        await startServer();
        await cancelShutdown();
        createWindow();
        app.on("activate", function () {
            if (BrowserWindow.getAllWindows().length === 0) {
                createWindow();
            }
        });
    }
});

app.on("before-quit", async (event) => {
    await handleShutdown();
});

app.on("window-all-closed", async () => {
    if (process.platform !== "darwin") {
        app.quit();
    }
});
