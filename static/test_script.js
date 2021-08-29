import http from 'k6/http'
import { check, sleep } from "k6";
import { Counter, Rate } from "k6/metrics";

let ErrorCount = new Counter("errors");
let ErrorRate = new Rate("error_rate");
// export const options = {
//     stages: [
//         { duration: '10s', target: 100 },

//         { duration: '10s', target: 200 },

//         { duration: '10s', target: 300 },

//         { duration: '30s', target: 500 },
//         { duration: '30s', target: 500 },
//         { duration: '1m', target: 0 }
//     ],
// };

export const options = {
    vus: 500,
    duration: '1m'
}

function print(s) {
    console.log(s);
};

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function buildQuery(data) {
    const result = [];

    Object.keys(data)
        .forEach((key) => {
            const encode = encodeURIComponent;
            result.push(encode(key) + "=" + encode(data[key]));
        });

    return result.join("&");
}

export default function () {
    print("STARTING A USER LOOP ");
    print(`VU: ${__VU}  -  ITER: ${__ITER}`);
    const user_id = getRandomInt(500);
    // const info = get_csrf_token();
    log_in(user_id);
    //get_events();
    sleep(1);
}

// function get_csrf_token() {
//     const url = 'http://127.0.0.1/app_api/auth/identity';

//     const params = {
//         headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
//         timeout: "1m"
//     };
//     let res = http.get(url, params);
//     return { cookies: res.cookies.csrftoken[0].value, token: (JSON.parse(res.body).response_data.csrf) };
// }

function log_in(user_id) {
    const url = 'http://127.0.0.1/app_api/auth/login';
    let data = { username: 'admin' + user_id, password: 'admin' };
    const params = {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        timeout: "1m"
    };
    //print(`START - VU: ${__VU}  -  ITER: ${__ITER} ` + JSON.stringify(url));
    let res = http.post(url, data, params);

    let success = check(res, {
        "status is 200": r => r.status === 200
    });
    if (!success) {
        ErrorCount.add(1);
        ErrorRate.add(true);
    } else {
        ErrorRate.add(false);
    }
    print(`DONE - VU: ${__VU}  -  ITER: ${__ITER}. Time: ` + String(res.timings.duration));
}


function get_events() {
    let urlQuery = buildQuery
        ({
            page: getRandomInt(1000000)
        });
    const url = 'http://127.0.0.1/app_api/events?' + urlQuery;
    const params = {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' },
        timeout: "10s"
    };
    //print(`START - VU: ${__VU}  -  ITER: ${__ITER} ` + JSON.stringify(url));
    let res = http.get(url, params);
    let success = check(res, {
        "status is 200": r => r.status === 200
    });
    if (!success) {
        ErrorCount.add(1);
        ErrorRate.add(true);
    } else {
        ErrorRate.add(false);
    }
    print(`DONE - VU: ${__VU}  -  ITER: ${__ITER}. Time: ` + String(res.timings.duration));
}