$ErrorActionPreference = "Stop"

$installerUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$installerPath = "$env:TEMP\Miniconda3-latest-Windows-x86_64.exe"
$installDir = "$env:USERPROFILE\Miniconda3"

Write-Host "Downloading Miniconda installer..."
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

Write-Host "Installing Miniconda silently to $installDir..."
# The /S flag is for silent installation.
# The /AddToPath=1 flag adds Conda to the system PATH.
# The /RegisterPython=0 flag prevents it from registering as the system's default Python.
Start-Process -FilePath $installerPath -ArgumentList "/InstallationType=JustMe /RegisterPython=0 /S /D=$installDir" -Wait

Write-Host "Installation complete. Cleaning up installer..."
Remove-Item $installerPath

Write-Host "Adding Conda to current session PATH so we can use it immediately..."
$env:PATH = "$installDir\Scripts;$installDir\condabin;$installDir;$env:PATH"

Write-Host "Initializing Conda..."
conda init powershell

Write-Host "Creating 'rag_demo' environment with Python 3.10..."
conda create -n rag_demo python=3.10 -y

Write-Host ""
Write-Host "================================================================="
Write-Host "Miniconda has been installed and the 'rag_demo' environment created."
Write-Host "Please RESTART your PowerShell or VSCode terminal, then run:"
Write-Host "    conda activate rag_demo"
Write-Host "    pip install -r c:\xjp\代码\rag-demo\requirements.txt"
Write-Host "================================================================="
