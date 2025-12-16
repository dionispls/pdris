// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Полифилл для clearImmediate
if (typeof global.clearImmediate === 'undefined') {
  global.clearImmediate = (handle) => {
    if (handle && typeof handle === 'object' && handle._onImmediate) {
      clearTimeout(handle._onImmediate);
    }
  };
}

if (typeof global.setImmediate === 'undefined') {
  global.setImmediate = (fn, ...args) => {
    return setTimeout(() => fn(...args), 0);
  };
}
