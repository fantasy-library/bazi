from lunar_python import Solar
s = Solar.fromYmdHms(2025,1,1,0,0,0)
l = s.getLunar()
try:
    table = l.getJieQiTable()
    print('type table:', type(table))
    for k in table:
        print('key repr:', repr(k))
        jq = table[k]
        print('  value type:', type(jq))
        if hasattr(jq, 'getName'):
            print('  name:', jq.getName())
        if hasattr(jq, 'getSolar'):
            print('  solar:', jq.getSolar().toYmdHms())
    nxt = l.getNextJieQi(True)
    print('getNextJieQi type:', type(nxt))
    if hasattr(nxt, 'getName'):
        print('next name:', nxt.getName())
    if hasattr(nxt, 'getSolar'):
        print('next solar:', nxt.getSolar().toYmdHms())
except Exception as e:
    print('error', e)
