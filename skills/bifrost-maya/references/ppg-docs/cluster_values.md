# Cluster Values
Lets you build groups of values that are similar.<br>
Example: <br>
Face IDs must be grouped based on the Y-position of the face centers.
- The face IDs are connected to `Values to Cluster`.
- The Y component of the corresponding face centers is connected to `Cluster Value`.
- All face IDs whose Y position is within the tolerance are grouped and output as a 2-dimensional array.
- This can also be used for strings, identical strings are grouped together.

## Inputs

### Values to Cluster
Array that you want to divide into groups.<br>
This can be any type.

### Cluster Value
Array of `scalar values` or `strings`, same order as `Values to Cluster`.<br>
Values within 'Tolerance' (or equal strings) will be grouped together.
	
### Tolerance
Values of the array `Cluster Value` are grouped if they differ no more than `Tolerance`.<br>
NOTE: this only works for numerical values of `Cluster Value`.

### Remainder Propagation
Uses a "smoother" way to cluster numeric values.<br>
Instead of only using the difference between the first value in a group and the rest of the array, a "remainder" from the last group is taken into account, resulting in a more "organic" (i.e. irregular) grouping.<br>
NOTE: this only works for numerical values of `Cluster Value`.

### Descending Order
Reverse the sorting of the `Cluster Value`.

## Outputs

### Clustered Values
2-dimensional array of all members of 'Values to Cluster'.<br>
Such a 2-dimensional array can be processed in a loop and also used with the node 'pattern_rename'.
