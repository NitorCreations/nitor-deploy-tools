## Working with TOTP MFA tokens

NDT includes tools to import, use and backup TOTP MFA tokens. Notably the `ndt assume-role` command
can use as an argument a name of an MFA token to make it easy to assume roles that require TOTP
MFA authentication.

### Importing

It is recommended that you import MFA codes from whatever place offers them to NDT first and then
use that to import the code to whatever other device that needs it. Importing is done with `ndt mfa-add-code`.
For the AWS console you would start by adding the MFA device to the IAM user
(IAM -> Users -> [Find user] -> Security credentials -> Assigned MFA device -> Edit) and choosing
"A virtual MFA device". Clicking "Next Step" twice will give you the qr code of the shared secret
and clicking "Show secret key for manual configuration" will give you the shared secret as text,
which is what ndt needs.

You can now go to the terminal and type in `ndt mfa-add-code -i mytokenname`. The name you give
here is the one you will be using on the command line to generate codes when needed so make
it easy to type and memorable. Ndt will ask for the secret that you can then cut and paste from
the console to the terminal. Next ndt will give you two consecutive codes that you can then
paste back into the console. Once this is done, ndt will still ask you for the ARN of the MFA
device, which is needed to interact with the api calls that use the token. If you are adding
a non-AWS token you can ignore this.

Ndt saves the token in `~/.ndt/mfa_mytokenname` and the secret is encrypted with a key that is
derived from your computers uuid. This means that those files are only usable on the machine
that you added the codes on.

### Using

The simplest use of the code is getting a TOTP code from the command line by calling `ndt mfa-code mytokenname`
The code printed can then be copied into whatever place is requesting it. Another very
handy use is to pass it to `ndt assume-role` to make assuming roles that require MFA easy.

A common practice is to create a sourceable file somewhere on your PATH (maybe `~/bin/`?)
that makes assuming roles just a matter of sourcing that file. Say you were to create the file
`~/bin/extadmin` (and `~/bin/` is on your PATH):

```bash
#!/bin/bash
export AWS_DEFAULT_REGION=eu-west-1 AWS_PROFILE=myprofile
unset AWS_SESSION_TOKEN AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
eval $(ndt assume-role -t mytokenname arn:aws:iam::223587298868:role/EXTAdmin)
unset AWS_PROFILE AWS_DEFAULT_PROFILE
```

Then assuming that role would simply be typing `. extadmin` in the terminal. That would also
be protected by the mfa codes that are only usable on your computer.

### Backing up

There are two ways to back up your tokens. The tokens will not be usable directly on any
other computer and that includes a re-installed OS on the same computer.
`ndt mfa-backup`, given an encryption password, will print out your tokens as an encrypted
string that contains decrypted secrets of all your tokens. You can put that then in a file
and store that in a safe place in case you need to recreate the tokens at some point.

The other way is to generate a QR code for each token and import them that way into another
device. The code is simply printed to the terminal with `ndt mfa-qrcode mytokenname`
