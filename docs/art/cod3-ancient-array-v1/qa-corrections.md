# Native QA corrections, all rejected runs retained

- Silverfall standalone first run: detector assumed positive blue change; translucent water darkens daytime blue sky. Image was visible; changed detection uses cyan shift.
- Silverfall standalone second run: moving vanilla rain produced sparse changed pixels. Require coherent 16x16 tiles (224 matching pixels); absence threshold stays 300.
- Combined v1: ancient-array far silhouette visually too narrow. Production core half-width .12 -> .24, alpha .48 -> .62; broad outer half-width .5 -> .6. Rebuilt and reran all 15 server tests.
- Combined v2: detector red-minus-blue >5 counted gold caps but missed translucent jade cores. Screenshot comparison shows 2058 correct green-excess core pixels, versus 152 under old predicate. Updated predicate; positive threshold stays 200.
- Combined v3: silverfall near-plane camera stands inside the main curtain and faces away from both secondary curtains. Screenshot is clear sky/terrain with no screen-filling wall. This case now explicitly expects absence; the 24-block near view still must be visible. No production geometry was changed for this correction.

No rejected native run counts as accepted. Final native evidence must come from a full successful run and manual screenshot review.
