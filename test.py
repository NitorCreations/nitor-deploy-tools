import nitor_deploy_tools

keyArn = nitor_deploy_tools.get_cf_params("vault")['keyArn']
enc = nitor_deploy_tools.encrypt(keyArn, b'Data')
print nitor_deploy_tools.decrypt(enc['dataKey'], enc['cipherText'])
