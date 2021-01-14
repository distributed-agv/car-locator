local car_id = ARGV[1]
local nonce = ARGV[2]
local car_num = ARGV[3]
local poss = {ARGV[4], ARGV[5], ARGV[6], ARGV[7], ARGV[8]}

if redis.call('GET', 'status') then
    return
end
if nonce ~= redis.call('GET', 'nonce') then
    return
end
if redis.call('HGET', 'owner_map', poss[1]) then
    return
end

redis.call('SADD', 'car_ids', car_id)
if redis.call('SCARD', 'car_ids') == tonumber(car_num) then
    redis.call('SET', 'status', 'NORMAL')
end
if not poss[3] then
    redis.call('HSET', 'owner_map', poss[1], car_id)
    redis.call('HSET', 'owner_map', poss[2], car_id)
else
    for i, pos in ipairs(poss) do
        if pos then
            redis.call('HSETNX', 'owner_map', pos, car_id)
        end
    end
end
