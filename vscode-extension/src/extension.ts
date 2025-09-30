import * as cp from 'child_process';
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
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

export function deactivate() {}

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
    } catch (error) {
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
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to start LLM2SLM server: ${error}`);
    }
}

function executeCommand(command: string): Promise<string> {
    return new Promise((resolve, reject) => {
        cp.exec(command, { cwd: getWorkspaceRoot() }, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
            } else {
                resolve(stdout.trim());
            }
        });
    });
}

function getWorkspaceRoot(): string | undefined {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        return workspaceFolders[0].uri.fsPath;
    }
    return undefined;
}
