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
task t {
    command <<< > >> >>>
}''',

# string literal trick
r'''workflow w {
    String x = ""
    String x = "abc"
    String x = "~{1}"
    String x = "~{"ab~{""}c"}"
    String x = "a}bc~ { {} ~~~"
}''',
]
