grammar RegExp;

namedExpr : (name=IDENTIFIER '=')? child=expr;

expr : 'True'                                     # True

     | child=atom                                 # Atomic
     | '!' child=atom                             # NegAtomic
     | var=IDENTIFIER '<=' child=atom             # VarBind

     | 'exists' '{' args=idlist '}' child=expr    # Exists
     | child=expr '*'                             # Star
     | child=expr '+'                             # Plus
     | child=expr '?'                             # Question
     | left=expr ';' right=expr                   # Concat
     | left=expr '&' right=expr                   # Intersection
     | left=expr '|' right=expr                   # Union
     | '(' child=expr ')'                         # Grouping    
     ;

atom : name=IDENTIFIER                     # Prop
     | name=IDENTIFIER '(' args=idlist ')' # Pred
     ;

idlist : param=IDENTIFIER (',' param=IDENTIFIER)*;


IDENTIFIER : [_a-zA-Z][_a-zA-Z0-9]*;

NUMBER: DIGIT | (DIGIT_NOT_ZERO DIGIT+);

WS         : [ \r\n\t]+ -> channel (HIDDEN);

fragment DIGIT: ('0'..'9');
fragment DIGIT_NOT_ZERO: ('1'..'9');
