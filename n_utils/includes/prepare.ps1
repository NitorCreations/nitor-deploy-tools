$url = "https://download.microsoft.com/download/7/9/6/796EF2E4-801B-4FC4-AB28-B59FBF6D907B/VCForPython27.msi"
$output = "C:\nitor\VCForPython27.msi"
(New-Object System.Net.WebClient).DownloadFile($url, $output)
Start-Process msiexec -ArgumentList @("/i", "C:\nitor\VCForPython27.msi", "/passive", "/quiet") -NoNewWindow -Wait

pip install -U pip setuptools awscli boto3 nitor-deploy-tools
