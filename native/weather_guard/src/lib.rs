// 요청 도시와 기상 격자의 대권 거리를 계산해 다른 지역의 날씨 혼입을 막습니다.
#[no_mangle]
pub extern "C" fn orbit_weather_distance(lat: f64, lon: f64, grid_lat: f64, grid_lon: f64) -> f64 {
    if ![lat, lon, grid_lat, grid_lon].iter().all(|v| v.is_finite())
        || lat.abs() > 90.0 || grid_lat.abs() > 90.0
        || lon.abs() > 180.0 || grid_lon.abs() > 180.0 { return -1.0; }
    let a = ((grid_lat-lat).to_radians()/2.0).sin().powi(2)
        + lat.to_radians().cos()*grid_lat.to_radians().cos()
        *((grid_lon-lon).to_radians()/2.0).sin().powi(2);
    6371.0088 * 2.0 * a.clamp(0.0, 1.0).sqrt().asin()
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn identical() { assert_eq!(orbit_weather_distance(37.27818,127.03164,37.27818,127.03164),0.0); }
    #[test] fn different_city() { let d=orbit_weather_distance(37.27818,127.03164,37.5665,126.978); assert!(d>30.0 && d<35.0); }
    #[test] fn invalid() { assert_eq!(orbit_weather_distance(f64::NAN,0.0,0.0,0.0),-1.0); assert_eq!(orbit_weather_distance(91.0,0.0,0.0,0.0),-1.0); }
    #[test] fn date_line() { assert!(orbit_weather_distance(0.0,179.99,0.0,-179.99)<3.0); }
}
