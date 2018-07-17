t = [
r'''workflow w {}''',

# basic workflow
r'''workflow w {
	input { String abc = 1 }
    Int abc = false
    call xyz
    Int abc = def
    call xyz {input {a = "a"}}
    output { String xyz = 2 }
}''',

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
    String x = ""
    String x = "abc"
    String x = "~{1}"
    String x = "~{"ab~{""}c"}"
    String x = "a}bc~ { {} ~~~"
}''',

# types
r'''workflow w {
    input {
        Int a
        Float b
        Boolean c
        String d
        File e
        Array[Int] f
        Map[String, Int] g
        Map[Array[Float], Map[Boolean, File]] g
    }
}''',

# expressions
r'''workflow w {
input {
    Int x = (1)
    Int x = 1.1
    Int x = 1[1]
    Int x = x(1)
    Int x = x(1,1)
    Int x = !1
    Int x = -1
    Int x = if 1 then 1 else 1
    Int x = 1 * 1
    Int x = 1 % 1
    Int x = 1 / 1
    Int x = 1 + 1
    Int x = 1 - 1
    Int x = 1 < 1
    Int x = 1 <= 1
    Int x = 1 > 1
    Int x = 1 >= 1
    Int x = 1 == 1
    Int x = 1 != 1
    Int x = 1 && 1
    Int x = 1 || 1
    Int x = {}
    Int x = {1:1}
    Int x = {1:1, 1:1}
    Int x = []
    Int x = [1]
    Int x = [1,1]
    Int x = 1
    Int x = x
}}''',
r'''workflow w {
input {
    String x = "~abc~~~xyz"
    String x = " ~{1} abc "
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
    String a = "~{"a"}"
}}''',
]
