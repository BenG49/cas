Fix get_pattern_matches: superpositions
- for each pattern where there are multiple options, have dictionary store all options in a tuple
- if pattern appears again:
  - look through possibilities and choose one that exists in current options
  - collapse all options in dictionary, including mutually exclusive options
    - how do i know if its definitely mutually exclusive? might just be coincidentally same options -- edge case though
