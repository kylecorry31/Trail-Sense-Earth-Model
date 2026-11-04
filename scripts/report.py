def print_stretch(name, coefficients, formula="value = pixel / a - b"):
    """Prints the coefficients of a stretch (see Stretch) for the app."""
    print(f"{name} ({formula})")
    print("    a:", [c["a"] for c in coefficients])
    # + 0.0 turns -0.0 into 0.0
    print("    b:", [c["b"] + 0.0 for c in coefficients])


def kotlin_map(name, entries):
    """A Kotlin map from the code of a key to the code of a value."""
    lines = [f"private val {name} = mapOf("]
    lines += [f"    {key} to {value}," for key, value in entries.items()]
    lines.append(")")
    return "\n".join(lines)


def kotlin_list(name, rows):
    """A Kotlin list of lists, from the code of each item."""
    lines = [f"private val {name} = listOf("]
    lines += [f"    listOf({', '.join(str(item) for item in row)})," for row in rows]
    lines.append(")")
    return "\n".join(lines)
