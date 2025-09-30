"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const cp = __importStar(require("child_process"));
const vscode = __importStar(require("vscode"));
function activate(context) {
    console.log('LLM2SLM extension is now active!');
    // Register the convert command
    const convertCommand = vscode.commands.registerCommand('llm2slm.convert', async () => {
        await runConvertCommand();
    });
    // Register the infer command
    const inferCommand = vscode.commands.registerCommand('llm2slm.infer', async () => {
        await runInferCommand();
    });
    // Register the serve command
    const serveCommand = vscode.commands.registerCommand('llm2slm.serve', async () => {
        await runServeCommand();
    });
    context.subscriptions.push(convertCommand, inferCommand, serveCommand);
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;
async function runConvertCommand() {
    // Get model name from user input
    const modelName = await vscode.window.showInputBox({
        prompt: 'Enter the model name to convert',
        placeHolder: 'e.g., gpt-3.5-turbo, llama-7b, etc.',
        validateInput: (value) => {
            if (!value || value.trim().length === 0) {
                return 'Model name is required';
            }
            return null;
        }
    });
    if (!modelName) {
        return; // User cancelled
    }
    // Create or show terminal
    const terminal = vscode.window.createTerminal('LLM2SLM Convert');
    terminal.show();
    // Run the convert command
    const command = `llm2slm convert --model "${modelName}" --size small --quant int4`;
    terminal.sendText(command);
}
async function runInferCommand() {
    try {
        // Run the inference command
        const command = 'llm2slm test --input "hello"';
        const result = await executeCommand(command);
        // Show result in notification
        vscode.window.showInformationMessage(`LLM2SLM Inference Result: ${result}`);
    }
    catch (error) {
        vscode.window.showErrorMessage(`LLM2SLM Inference failed: ${error}`);
    }
}
async function runServeCommand() {
    try {
        // Create or show terminal
        const terminal = vscode.window.createTerminal('LLM2SLM Server');
        terminal.show();
        // Run the serve command
        const command = 'llm2slm serve --ui';
        terminal.sendText(command);
        // Wait a moment for server to start, then open browser
        setTimeout(() => {
            vscode.env.openExternal(vscode.Uri.parse('http://localhost:8000'));
        }, 3000);
        vscode.window.showInformationMessage('LLM2SLM server starting... Browser will open automatically.');
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to start LLM2SLM server: ${error}`);
    }
}
function executeCommand(command) {
    return new Promise((resolve, reject) => {
        cp.exec(command, { cwd: getWorkspaceRoot() }, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
            }
            else {
                resolve(stdout.trim());
            }
        });
    });
}
function getWorkspaceRoot() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        return workspaceFolders[0].uri.fsPath;
    }
    return undefined;
}
//# sourceMappingURL=extension.js.map