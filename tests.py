t = [
# basic workflow
r'''workflow { 
	input { String abc = 1 }
    Int abc = false
    call xyz
    Int abc = def
    call xyz {input: a = "a"}
    output { String xyz = 2 }
}''',

# multipe >>> aren't greedy
r'''workflow {}
task {
    command <<< >>>
}
task {
    command <<<
    xyz abc

    xyz abc
    >>>
}
''',

# >>> with space doesnt trick
r'''workflow {}
task {
    command <<< > >> >>>
}'''
]