let map = fn(arr, f) {
	let iter = fn(arr, accum) {
		if (len(arr) == 0) {
			return accum;
		}
		else {
			return iter(rest(arr), push(accum, f(first(arr))));
		}
	};
	iter(arr, []);
};

let a = [1, 2, 3, 4];
let double = fn(x) { x + x };
map(a, double);
