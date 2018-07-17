t = [
r'''workflow w {}''',

# basic workflow
r'''workflow w {
	input { String a = "a" }
    Int ab = 1
    call xyz
    Int abc = ab + 1 + ab
    output { String abcd = "done" }}
''',

# multipe >>> aren't greedy
r'''workflow w {}
task t {
    command <<< >>>
}
task t {
    command <<<
    xyz abc

    xyz abc
    >>>
}
''',

# >>> with space doesnt trick
r'''workflow w {}
task t { command <<< >>> }
task t { command <<< > > > >>> }
task t { command <<< > >> > >>> }
task t { command <<< a> b>> >c >>> }
''',

# string literal trick
r'''workflow w {
    String a = ""
    String b = "abc"
    String c = "~{""}"
    String d = "~{"ab~{1 + ""}c"}"
    String e = "a}bc~ { {} ~~~"
}''',

# types
r'''workflow w {
    input {
        Int a = 1
        Float b = 1.0
        Boolean c = false
        String d = "a"
        # File e = "b"
        Array[Int] f
        Map[String, Int] g
        Map[Array[Float], Map[Boolean, File]] h
    }
}''',

# expressions
r'''workflow w {
input {
    Int a = (1)
    # Int b = 1.1
    # Int c = 1[1]
    # Int d = x(1)
    # Int e = x(1,1)
    Boolean f = false && true
    Int g = -1
    Int h = if true then 1 else 1
    Int i = 1 * 1
    Int j = 1 % 1
    Int k = 1 / 1
    Int l = 1 + 1
    Int m = 1 - 1
    Boolean n = 1 < 1
    Boolean o = 1 <= 1
    Boolean p = 1 > 1
    Boolean q = 1 >= 1
    Boolean r = 1 == 1
    Boolean s = 1 != 1
    Int t = 1 && 1
    Int u = 1 || 1
    Int v = {}
    Int w = {1:1}
    Int x = {1:1, 1:1}
    Int y = []
    Int A = [1]
    Int B = [1,1]
    Int C = 1
    Int D = x
}}''',
r'''workflow w {
input {
    String x = "~abc~~~xyz"
    String x = " ~{"1"} abc "
}}''',
r'''workflow w {
input {
    Int x = 1 + 2
    Int y = 1 + x
    String a = "3" + "4"
    String b = a + "5"
}}''',
r'''workflow w {
input {
    String a = "~{"a" + 1}"
}}''',
]
