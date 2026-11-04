# Worked example: choosing the WebP quality of each temperature image

This walks through how `generate-temperature-model.py` picks a quality for each image, using a small made-up
example. The real run has 18 images (9 for the highs, 9 for the lows), 12 qualities each, and a 150 KB budget. The
numbers below are invented to keep the arithmetic readable, and sizes are in KB (the code works in bytes, so its
penalty is per byte rather than per KB).

## The setup

Suppose there are only three images, three qualities, and a 100 KB budget:

- **A**: the mean (importance 1, since it applies to every month)
- **B**: the first harmonic (importance 0.5)
- **C**: the fourth harmonic (importance 0.5)

## Step 1: encode every image at every quality

`WebpQualityOptions` encodes each image at each quality, decodes the result, undoes the stretch
(`value = pixel / a - b`), and measures the squared error against the original, weighted by cos(latitude). The cost
of an option is `importance * squared_error`.

| Image | Quality | Size (KB) | Squared error | Cost |
|-------|---------|-----------|---------------|------|
| A     | 30      | 20        | 4.0           | 4.00 |
| A     | 60      | 40        | 1.0           | 1.00 |
| A     | 90      | 70        | 0.2           | 0.20 |
| B     | 30      | 10        | 2.0           | 1.00 |
| B     | 60      | 22        | 0.6           | 0.30 |
| B     | 90      | 45        | 0.3           | 0.15 |
| C     | 30      | 5         | 0.2           | 0.10 |
| C     | 60      | 9         | 0.1           | 0.05 |
| C     | 90      | 20        | 0.08          | 0.04 |

Highest quality everywhere would be 70 + 45 + 20 = 135 KB, which is over budget, so something has to give.

## Step 2: price a byte

`fit_to_budget` makes each image pick the option with the lowest `cost + penalty * size`. The penalty is how much
error is acceptable in exchange for saving one KB. Each image decides on its own, so no image is ever compared with
another directly.

Take image A at a penalty of 0.05:

| Quality | cost + 0.05 * size |
|---------|--------------------|
| 30      | 4.00 + 1.00 = 5.00 |
| 60      | 1.00 + 2.00 = 3.00 |
| 90      | 0.20 + 3.50 = 3.70 |

Quality 60 wins. The penalty at which an image switches between two qualities is where their totals tie. For
example, A switches from 60 to 30 when `1.00 + 40p = 4.00 + 20p`, so `p = 0.15`.

Doing this for every image gives the switch points below (the penalty above which the image drops to the next quality):

| Image | 90 -> 60 above | 60 -> 30 above |
|-------|----------------|----------------|
| A     | 0.0267         | 0.15           |
| B     | 0.0065         | 0.0583         |
| C     | 0.0009         | 0.0125         |

As the penalty rises, the images drop in this order: C (90 to 60), then B (90 to 60), then C (60 to 30), then A.
Image C goes first because it has little error to lose and saves a lot of bytes (20 KB down to 9). The mean, A, goes
last because its error climbs steeply as quality falls.

The total size at each penalty range:

| Penalty range    | A  | B  | C  | Total (KB) | Fits in 100? |
|------------------|----|----|----|------------|--------------|
| below 0.0009     | 90 | 90 | 90 | 135        | no           |
| 0.0009 to 0.0065 | 90 | 90 | 60 | 124        | no           |
| 0.0065 to 0.0125 | 90 | 60 | 60 | 101        | no           |
| 0.0125 to 0.0267 | 90 | 60 | 30 | 97         | yes          |
| 0.0267 to 0.0583 | 60 | 60 | 30 | 67         | yes          |
| 0.0583 to 0.15   | 60 | 30 | 30 | 55         | yes          |
| above 0.15       | 30 | 30 | 30 | 35         | yes          |

The goal is the lowest penalty that still fits, because a lower penalty means less error. That is 0.0125, just
above the 101 KB row.

## Step 3: find that penalty by binary search

The code does not build the table above. It searches between 1e-12 and 1e3, halving the range on a log scale (the
geometric mean) 80 times. If the total is over budget, the penalty is too low, so it raises the lower bound.
Otherwise it lowers the upper bound.

| Try (penalty) | Picks (A, B, C) | Total (KB) | Result                |
|---------------|-----------------|------------|-----------------------|
| 0.0000316     | 90, 90, 90      | 135        | over, raise the floor |
| 0.178         | 30, 30, 30      | 35         | fits, lower the ceiling |
| 0.00237       | 90, 90, 60      | 124        | over                  |
| 0.0205        | 90, 60, 30      | 97         | fits                  |
| 0.00697       | 90, 60, 60      | 101        | over                  |
| 0.01195       | 90, 60, 60      | 101        | over                  |
| 0.01565       | 90, 60, 30      | 97         | fits                  |

It keeps narrowing toward 0.0125. The code returns the picks at the final upper bound, which always fits.

## The result

| Image | Quality | Size (KB) |
|-------|---------|-----------|
| A     | 90      | 70        |
| B     | 60      | 22        |
| C     | 30      | 5         |
| Total |         | 97        |

Total cost is 0.20 + 0.30 + 0.10 = 0.60.

For comparison, a uniform quality of 60 would take 40 + 22 + 9 = 71 KB at a cost of 1.00 + 0.30 + 0.05 = 1.35. The
optimizer spends the extra 26 KB on the mean, where it reduces error the most, and takes the savings from the
harmonic that has the least to lose.

The total (97 KB) is below the budget because only three qualities exist. The next step up for any image would go
over: raising C from 30 to 60 gives 101 KB. With 12 qualities per image in the real run, the total lands much closer
to 150 KB.

## Why this works

At the chosen penalty, every image sits at the point where one more KB would buy back less error than the penalty
says it is worth, and one less KB would cost more error than it saves. No move of bytes from one image to another can
lower the total cost, which is the condition for an optimal split of a fixed budget. This holds for the quality
options on each image's lower convex hull. An option that is both bigger and worse than another is never chosen at
any penalty.
