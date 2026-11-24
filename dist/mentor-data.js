window.MentorXData = {
  model: {
    name: 'Logistic Regression',
    featureNames: ['minutes_stuck', 'repeated_attempts', 'hint_requests', 'breakthroughs', 'current_hint_level', 'difficulty'],
    mean: [25.31245899289622, 1.7755555555555556, 1.1151111111111112, 0.6453333333333333, 2.020888888888889, 2.013333333333333],
    scale: [16.585048543426982, 1.3286008606476083, 1.050541917767991, 0.7879582617259788, 1.398096836929431, 0.8092795149596433],
    coefficients: [0.913031952519092, 0.674255942663019, 0.5816694472675996, -0.7677613474439084, 0.16324458494686198, 0.18428972183966222],
    intercept: 0.03868676958046873
  },
  interactive: {
    'two-sum': {
      title: 'Two Sum — find the pair, not just the answer.',
      context: 'Given an array of integers and a target, return the indices of two numbers that add up to the target.',
      topic: 'Arrays & Hashing', difficulty: 2,
      hints: [
        'For the current number, which value would complete the target?',
        'If the needed value appeared earlier, what information could help you find it quickly?',
        'Keep a lookup from each seen number to its index. Check target minus the current value before storing it.',
        'For each index and value: calculate the complement. If it is in the lookup, return both indices; otherwise store the current value.',
        'A hash-map lookup gives O(n) time overall. Checking before storing prevents using the same element twice.'
      ],
      concepts: [['hash map', 'dictionary', 'lookup', 'map'], ['complement', 'target -', 'target minus'], ['one pass', 'scan', 'iterate'], ['o(n)', 'linear time']]
    },
    'recursion-base-case': {
      title: 'Trust the function to solve the smaller story.',
      context: 'Explore how recursive calls reduce a problem until one simple case remains.',
      topic: 'Recursion', difficulty: 1,
      hints: [
        'What is the smallest input for which the answer needs no further recursive call?',
        'Each call should make the input smaller. What operation connects n to a smaller case?',
        'Use a base case for zero or one; otherwise combine n with the result for n minus one.',
        'If n is zero or one, return one. Otherwise return n multiplied by factorial of n minus one.',
        'The base case stops recursion and each call reduces n, giving O(n) time and O(n) call-stack space.'
      ],
      concepts: [['base case', 'zero or one', '0 or 1'], ['recursive', 'recursion'], ['n - 1', 'n-1', 'smaller'], ['o(n)', 'linear']]
    },
    'container-most-water': {
      title: 'Let the order do some of the thinking.',
      context: 'Use the sorted structure of data to eliminate possibilities with intent.',
      topic: 'Two Pointers', difficulty: 2,
      hints: [
        'Area depends on distance and the shorter height. Which part can improve when you move inward?',
        'If one line is shorter, moving the taller line cannot improve the limiting height. Which pointer should move?',
        'Keep left and right pointers, record the best area, and move the pointer at the shorter line.',
        'While left is before right: update area from width times the smaller height, then move the shorter pointer.',
        'Moving the shorter boundary is the only chance to increase the limit. Each pointer moves once: O(n) time.'
      ],
      concepts: [['two pointers', 'left and right', 'left/right'], ['shorter', 'smaller height'], ['move', 'inward'], ['o(n)', 'linear']]
    }
  },
  questions: [
    ['Arrays & Hashing', 'Two Sum', 'Easy', 'two-sum'], ['Arrays & Hashing', 'Contains Duplicate', 'Easy', 'contains-duplicate'], ['Arrays & Hashing', 'Valid Anagram', 'Easy', 'valid-anagram'],
    ['Two Pointers', 'Valid Palindrome', 'Easy', 'valid-palindrome'], ['Two Pointers', 'Two Sum II — Input Array Is Sorted', 'Medium', 'two-sum-ii-input-array-is-sorted'], ['Two Pointers', 'Container With Most Water', 'Medium', 'container-with-most-water'],
    ['Sliding Window', 'Best Time to Buy and Sell Stock', 'Easy', 'best-time-to-buy-and-sell-stock'], ['Sliding Window', 'Longest Substring Without Repeating Characters', 'Medium', 'longest-substring-without-repeating-characters'], ['Sliding Window', 'Longest Repeating Character Replacement', 'Medium', 'longest-repeating-character-replacement'],
    ['Stack', 'Valid Parentheses', 'Easy', 'valid-parentheses'], ['Stack', 'Min Stack', 'Medium', 'min-stack'], ['Stack', 'Evaluate Reverse Polish Notation', 'Medium', 'evaluate-reverse-polish-notation'],
    ['Binary Search', 'Binary Search', 'Easy', 'binary-search'], ['Binary Search', 'Search a 2D Matrix', 'Medium', 'search-a-2d-matrix'], ['Binary Search', 'Koko Eating Bananas', 'Medium', 'koko-eating-bananas'],
    ['Linked List', 'Reverse Linked List', 'Easy', 'reverse-linked-list'], ['Linked List', 'Merge Two Sorted Lists', 'Easy', 'merge-two-sorted-lists'], ['Linked List', 'Linked List Cycle', 'Easy', 'linked-list-cycle'],
    ['Trees', 'Invert Binary Tree', 'Easy', 'invert-binary-tree'], ['Trees', 'Maximum Depth of Binary Tree', 'Easy', 'maximum-depth-of-binary-tree'], ['Trees', 'Diameter of Binary Tree', 'Easy', 'diameter-of-binary-tree'],
    ['Graphs', 'Number of Islands', 'Medium', 'number-of-islands'], ['Graphs', 'Clone Graph', 'Medium', 'clone-graph'], ['Graphs', 'Course Schedule', 'Medium', 'course-schedule'],
    ['Dynamic Programming', 'Climbing Stairs', 'Easy', 'climbing-stairs'], ['Dynamic Programming', 'House Robber', 'Medium', 'house-robber'], ['Dynamic Programming', 'Coin Change', 'Medium', 'coin-change'],
    ['Backtracking', 'Subsets', 'Medium', 'subsets'], ['Backtracking', 'Combination Sum', 'Medium', 'combination-sum'], ['Backtracking', 'Generate Parentheses', 'Medium', 'generate-parentheses']
  ].map(([topic, title, difficulty, slug]) => ({
    topic, title, difficulty, slug, url: `https://leetcode.com/problems/${slug}/`,
    interactive: ['two-sum', 'container-most-water'].includes(slug)
  }))
};
