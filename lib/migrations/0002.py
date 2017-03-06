
import json


@migrate.update_collection('package_version')
def convert_manifest_to_string(obj):
  """
  Manifests are now stored as strings instead of Documents because MongoDB
  does not allow dots in field names, which can be the case in Node.py
  package manifests.
  """

  obj['manifest'] = json.dumps(obj['manifest'], indent=2, sort_keys=True)
