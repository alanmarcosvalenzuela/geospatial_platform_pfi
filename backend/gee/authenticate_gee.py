import ee 

service_account = 'terradata@terradata-403013.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'gee/private-key.json')

ee.Initialize(credentials)
