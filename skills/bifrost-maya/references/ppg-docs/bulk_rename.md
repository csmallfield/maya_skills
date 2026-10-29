# Bulk Rename
Rename multiple face groups.<br>

## Inputs

### Mesh
The input geometry with face tags.<br>

### Rename Face Tags
Fan-in string array input.<br><br>
Connect multiple string value nodes that contain a renaming in the form:<br>
`face tag expression(s) : new_name`<br>
- `face tag expression` is a space separated list of face tags which may contain "\*" (asterisk) wildcards.<br>
- `new_name` is the face tag (existing or new) that these faces are assigned to.<br>

Each string can assign ONE new name  to a selection of faces.<br>
Example:<br>
`*win* transp* face36 : glas` selects all faces that have matching tags (\*win\*, transp\*, face36) and renames them to `glas`.

