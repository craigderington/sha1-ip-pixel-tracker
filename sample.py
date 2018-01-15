import json

response = "[{\"FirstName\":\"ricahrd\",\"LastName\":\"Lynn\",\"Address\":\"3036 REGATTA DR\",\"City\":\"SARASOTA\",\"state\":\"FL\",\"ZipCode\":\"34231\",\"Zip4\":\" \",\"YEAR\":\"2008\",\"MAKE\":\"Ford\",\"MODEL\":\"Escape\",\"InferredCreditScore\":\"550-599\",\"EMail\":\"tplynn1616@verizon.net\",\"Cell\":\"3863147689\",\"IP\":\"107.72.164.122\",\"Dealer\":\"DMS\",\"Product\":\"earl\",\"JobNumber\":\"29416\",\"CampaignID\":\"dms34689\",\"VendorID\":\"DMS\"}]"
parsed_data = json.loads(response)


print("The M1 Values are: ")
print('First & Last Name: {} {}'.format(parsed_data[0]['FirstName'], parsed_data[0]['LastName']))
print('IP: {}'.format(parsed_data[0]['IP']))
print('Address {}'.format(parsed_data[0]['Address'], parsed_data[0]['City'], parsed_data[0]['state'], parsed_data[0]['ZipCode']))
print('Phone: {}'.format(parsed_data[0]['Cell']))
print('Email: {}'.format(parsed_data[0]['EMail']))
print('Automotive Details: {} {} {}'.format(parsed_data[0]['YEAR'], parsed_data[0]['MAKE'], parsed_data[0]['MODEL']))
print('Inferred Credit Score: {}'.format(parsed_data[0]['InferredCreditScore']))


