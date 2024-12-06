$scriptPath = "d:/D/ultima milla/2024/MKT 2024/licitometro/licitometro91/project/CascadeProjects/windsurf-project/licitometro/backend/recon/start_services.sh"

# Establecer permisos de ejecución
$acl = Get-Acl $scriptPath
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    [System.Security.Principal.WindowsIdentity]::GetCurrent().User,
    "ExecuteFile",
    "Allow"
)
$acl.SetAccessRule($rule)
$acl | Set-Acl $scriptPath

Write-Host "Permisos de ejecución establecidos para start_services.sh"
