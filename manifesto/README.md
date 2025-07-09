# The EdHub code quality manifesto

This document specifies the standards by which the code in this repository is
to be written, maintained, and reviewed. These standards are mutually agreed
upon by the members of the EdHub development team.

The standards are subject to discussion.

If an existing piece of code does not follow the rules described here, a
**GitHub issue** is to be created.

If a piece of code proposed for merging is considered to not follow the rules
described here, the problem is to be pointed out to the assignee and **resolved
before merging**.

## Database

*To be discussed*

### Signatures

I have read and understood the rules and will follow them. If applying the rules
results in a clearly suboptimal solution, I will immediately consult the other
team members to have the standards changed.

- [ ] Askar Dinikeev
- [ ] Gleb Popov
- [ ] Timur Usmanov

## Backend

### 1. Single Responsibility

All functions have a single responsibility, which is clear from the name, and
operate within a single layer of abstraction. That makes the functions reusable.

### 2. Modularity 

The three major modules of the program are `routers`, `logic`, and `sql`.

1. The `routers` module defines FastAPI endpoints and uses `logic` functions to
   query and control the state of the web service. The endpoint handlers must
   contain no complicated logic.

2. The `logic` module defines **reusable** abstractions (functions) that control
   or query the state of the web service in a non-trivial way. In particular,
   the `logic` functions must not care about the identity of the client calling
   a web API endpoint. Moreover, SQL code is not to be used in this module.

3. The `sql` module defines **reusable** functions that query the database in a
   trivial way. In particular, no additional checks need to be performed that
   ensure the operation should make sense in any context.

### 3. Clarity

*This is an extension of rule 1 (**single responsibility**).*

All functions always annotate argument and return types. If the return type is
too complicated to annotate, create a *data transfer class* right beside the
function and return instances of it. Functions in modules other than the
`routers` module never return dictionaries used as JSON objects.

In particular, functions in `logic` **NEVER** return {"success": True} or
similar. Dictionaries with one key should be replaced with their values,
dictionaries with more than one key must be turned into class instances or
tuples.

### 4. HTTP errors are subclasses

All errors in `logic` (including `constraints`) or `routers` are raised (thrown)
as respective class instances, not as `HTTPException`. If a new kind of error is
introduced, a new class must be declared.

### 5. Permissions are a web concern

*This is an extension of rule 2 (**modularity**).*

**ALL** access permission checking is done in the `routers` code, never in
`logic`. Access permission checking in the `routers` code is always done
through `constraints.py`.

`logic` functions never receive `user_email` that is meant to be used for
permission checking.

### 6. Databases are abstractions

Define and use databases like so:
```python
# somewhere in `db/conn.py`
sysdb = Database("system_db", "5432", "edhub", "postgres", "12345678")
filedb = Database("storage_db", "5432", "edhub_storage", "postgres", "12345678")

# in `routers/*.py`
with routers.conn.sysdb.connect() as conn:
```
Benefits: easy to make connection pools and otherwise improve on the system

### 7. Pass connections

In functions that handle endpoints, obtain connections to databases as shown in
rule 6 (**databases are abstractions**). Pass connections to `logic` functions,
from there to `sql` functions. In those, create cursors for querying.

Benefits: no bugs related to not fetching every returned row from the SQL query.

### 8. Comments are redundant

*This is an extension of rule 1 (**single responsibility**).*

If an internal function's behaviour is unclear, here are the possible solutions
the author should consider, in order:

1. Renaming the function
2. Implementing a different function
3. Writing a docstring

Comments are reserved for marking incomplete code with a `TODO` line or warning
someone of the caveats of a function's implementation if a careless refactoring
may cause a bug.

### 9. No redundant functions

If a function **in the commit history** may be useful in the future but is not
currently needed, it should be removed from the codebase. If it is ever needed
again, it may be restored from the history.

Benefits: the fewer functions there are, the easier the code becomes.

### Signatures

I have read and understood the rules and will follow them. If applying the rules
results in a clearly suboptimal solution, I will immediately consult the other
team members to have the standards changed.

- [ ] Askar Dinikeev

- [ ] Gleb Popov

- [x] Timur Usmanov

## Frontend

*To be discussed*

### Signatures

I have read and understood the rules and will follow them. If applying the rules
results in a clearly suboptimal solution, I will immediately consult the other
team members to have the standards changed.

- [ ] Alina Suhoverkova

- [ ] Timur Struchkov
