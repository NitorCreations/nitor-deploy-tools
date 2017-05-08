param (
  [string]$drive
)
Get-WmiObject Win32_DiskDrive | % {
  $disk = $_
  $partitions = "ASSOCIATORS OF " +
                "{Win32_DiskDrive.DeviceID='$($disk.DeviceID)'} " +
                "WHERE AssocClass = Win32_DiskDriveToDiskPartition"
  Get-WmiObject -Query $partitions | % {
    $partition = $_
    $drives = "ASSOCIATORS OF " +
              "{Win32_DiskPartition.DeviceID='$($partition.DeviceID)'} " +
              "WHERE AssocClass = Win32_LogicalDiskToPartition"
    Get-WmiObject -Query $drives | % {
      New-Object -Type PSCustomObject -Property @{

        TargetId    = $disk.SCSITargetId
        DiskNumber  = $disk.Index
        DriveLetter = $_.DeviceID
      }
    }
  }
} | Where-Object DriveLetter -eq $drive | ConvertTo-Xml -As String
