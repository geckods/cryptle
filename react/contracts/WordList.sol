// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.0 <0.9.0;

contract WordList {

    string[700] public wordList = ['STORM', 'ROUGH', 'WELSH', 'BASED', 'GOING', 'AGREE', 'BRAIN', 'ARRAY', 'SORRY', 'ALPHA', 'IDIOT', 'CREEK', 'EXIST', 'SPEED', 'BLAKE', 'CHINA', 'GRANT', 'QUEST', 'ARENA', 'SIZED', 'SPEAK', 'VALVE', 'BEGIN', 'ROUTE', 'FORTY', 'LYING', 'BACON', 'SWIFT', 'SOLVE', 'STEAM', 'LIVED', 'PUNCH', 'EVERY', 'MATCH', 'BRING', 'WOULD', 'VISIT', 'WORRY', 'GLORY', 'LARRY', 'JAPAN', 'LIVER', 'BASIS', 'MINOR', 'EXACT', 'ADULT', 'SADLY', 'OCEAN', 'SLIDE', 'STOCK', 'WHITE', 'SUPER', 'TRICK', 'BASES', 'STOOD', 'DEPTH', 'SMILE', 'GAINS', 'QUEEN', 'BLOOD', 'ENTER', 'OFTEN', 'DELAY', 'MERCY', 'FORTH', 'FAULT', 'BEGUN', 'STAYS', 'EMPTY', 'MODEL', 'BLUES', 'GREAT', 'NAKED', 'CABIN', 'LATER', 'FOCUS', 'FRONT', 'WORLD', 'PROVE', 'ANGLE', 'COVER', 'ALIVE', 'CHOSE', 'DRESS', 'SWISS', 'DEALT', 'MOTOR', 'SMART', 'GREEN', 'ERROR', 'TRAIL', 'SHAME', 'SKULL', 'FIFTH', 'INPUT', 'DREAM', 'ULTRA', 'FIGHT', 'LAURA', 'TOXIC', 'PROOF', 'BLANK', 'CROSS', 'ABUSE', 'MEANT', 'CHAIN', 'HUMOR', 'SANDY', 'BAKER', 'THING', 'MONEY', 'MAYBE', 'HABIT', 'CRASH', 'PLANE', 'GRAIN', 'SMALL', 'HENCE', 'OFFER', 'LAUGH', 'ELITE', 'EARTH', 'CLOUD', 'TRIBE', 'TOMMY', 'LOYAL', 'SINCE', 'TOTAL', 'FUNNY', 'PUSSY', 'POWER', 'VALID', 'ENDED', 'DRAMA', 'CHECK', 'FAVOR', 'THEME', 'APPLE', 'DRIVE', 'AFTER', 'BEACH', 'SNAKE', 'SHAPE', 'SPORT', 'PAPER', 'PRIDE', 'THOSE', 'BLAST', 'WROTE', 'YOUTH', 'CLAIM', 'AWAKE', 'THEIR', 'LAYER', 'POINT', 'CABLE', 'AHEAD', 'STORY', 'ADOPT', 'LEAST', 'KELLY', 'AWARE', 'WORKS', 'SAINT', 'AMONG', 'BITCH', 'GLOBE', 'SMELL', 'GUEST', 'COLOR', 'NOBLE', 'UNDER', 'EQUAL', 'TREND', 'ARMED', 'DIARY', 'INNER', 'COUCH', 'THIRD', 'TITLE', 'CLEAN', 'ORGAN', 'MOUTH', 'DEBUT', 'ADMIT', 'BURST', 'BELOW', 'BUNCH', 'BEING', 'DELTA', 'UNITY', 'BARRY', 'FEVER', 'BRAVE', 'CRACK', 'MONTH', 'LARGE', 'FIXED', 'ARGUE', 'PEACE', 'WORTH', 'ENJOY', 'STUCK', 'CHAOS', 'SILLY', 'CLOSE', 'STYLE', 'BLOCK', 'CATCH', 'HEART', 'DAIRY', 'SWEET', 'SQUAD', 'FINAL', 'PANTS', 'SHARP', 'MARRY', 'HOUSE', 'STRIP', 'THERE', 'ASIDE', 'SPACE', 'CARGO', 'CLOCK', 'REPLY', 'WASTE', 'STAFF', 'CHART', 'SHOWN', 'STILL', 'POUND', 'MIGHT', 'CRIME', 'LOGIC', 'TOPIC', 'VITAL', 'CHIPS', 'SHELL', 'FLEET', 'TIGHT', 'NEEDS', 'ALLOW', 'MIXED', 'TREAT', 'BRAND', 'ROYAL', 'ARROW', 'BLADE', 'WHILE', 'FLUID', 'SHORT', 'SWORD', 'ADDED', 'THINK', 'HORSE', 'DIDNT', 'BUILT', 'PHOTO', 'FLOOD', 'BOOTH', 'MOVIE', 'RAISE', 'SIZES', 'LUNCH', 'THANK', 'TRACK', 'SHEEP', 'BREAD', 'RIVER', 'COACH', 'UNION', 'SCARY', 'GRAND', 'FIELD', 'ABOUT', 'GUARD', 'TWEET', 'TASTE', 'SPENT', 'WORSE', 'PIECE', 'SMITH', 'GROWN', 'NORTH', 'GIVEN', 'SHAKE', 'AVOID', 'ESSAY', 'NOTED', 'REACT', 'PRESS', 'GHOST', 'TODAY', 'PIANO', 'VALUE', 'VOTER', 'SHOCK', 'TALES', 'HUMAN', 'HURRY', 'LOWER', 'OLDER', 'BOARD', 'FIRED', 'HOTEL', 'RURAL', 'NAVAL', 'SLEEP', 'JERRY', 'RALLY', 'TRUMP', 'CLEAR', 'ACTOR', 'YIELD', 'BOOTS', 'MORAL', 'TRACE', 'ROUND', 'LEWIS', 'PARTY', 'HONEY', 'SWEAT', 'COSTA', 'CLIFF', 'KNOCK', 'PLATE', 'PETER', 'GLASS', 'LOOSE', 'SIDES', 'SKILL', 'OUGHT', 'THESE', 'CREAM', 'APART', 'TRAIN', 'ORDER', 'PRIZE', 'AGENT', 'NERVE', 'FLESH', 'HAVEN', 'BLESS', 'VERSE', 'RIDGE', 'RADIO', 'FATAL', 'SALAD', 'ROCKY', 'BONUS', 'CURVE', 'MOUNT', 'NEWLY', 'BUDDY', 'EIGHT', 'SCORE', 'GOODS', 'RAPID', 'NEVER', 'CORPS', 'GRASS', 'COULD', 'ALONG', 'INTER', 'OCCUR', 'NURSE', 'MAJOR', 'TRIAL', 'SWING', 'CRUEL', 'BLAME', 'COLIN', 'MARIA', 'RIFLE', 'IDEAL', 'SOUTH', 'LEMON', 'INDEX', 'READY', 'PANEL', 'ALBUM', 'STATE', 'BASIC', 'GROSS', 'SOLAR', 'STEEL', 'STUDY', 'THATS', 'MARCH', 'RADAR', 'FUNDS', 'WRONG', 'JIMMY', 'SPRAY', 'DRILL', 'WHICH', 'CHEST', 'FORCE', 'LEASE', 'TOWER', 'LASER', 'DAILY', 'PRIME', 'SIXTH', 'SCREW', 'SAUCE', 'HONOR', 'CRAZY', 'BRICK', 'ANGRY', 'SHARK', 'MINES', 'ALONE', 'TABLE', 'WOUND', 'TEETH', 'WHOLE', 'TOUCH', 'BLOWN', 'CLIMB', 'COMES', 'BENCH', 'WATCH', 'ROBIN', 'RATED', 'IMAGE', 'SMOKE', 'ROBOT', 'PRINT', 'STEAL', 'MASON', 'YOUNG', 'BOBBY', 'CYCLE', 'SHIFT', 'SHALL', 'DRINK', 'MEDAL', 'FLASH', 'TWICE', 'QUITE', 'AWFUL', 'SLAVE', 'AWARD', 'FENCE', 'RELAX', 'BOOST', 'FULLY', 'REACH', 'SCALE', 'DANCE', 'SOLID', 'ABOVE', 'MAKER', 'UPSET', 'MUSIC', 'ANIME', 'WHERE', 'HOPED', 'LABOR', 'VIRUS', 'JUDGE', 'DEVIL', 'COAST', 'JUICE', 'QUIET', 'LIMIT', 'OLIVE', 'CHARM', 'GIANT', 'PATCH', 'STICK', 'FANCY', 'LABEL', 'BREAK', 'STUFF', 'ASSET', 'TRUCK', 'JOINT', 'SENSE', 'CRUSH', 'FIFTY', 'BLACK', 'EARLY', 'QUICK', 'TWIST', 'GUILT', 'REFER', 'THEFT', 'LOVER', 'USAGE', 'DIRTY', 'SOUND', 'GENRE', 'DYING', 'CHASE', 'SPEND', 'GRADE', 'SPOKE', 'SETUP', 'PERRY', 'GRAVE', 'VENUE', 'LOCAL', 'GUESS', 'ROGER', 'THROW', 'SCOPE', 'BROKE', 'OTHER', 'NOISE', 'STAKE', 'VILLA', 'HENRY', 'SPELL', 'BILLY', 'EAGLE', 'BUILD', 'AUDIO', 'KNOWN', 'FRESH', 'ALARM', 'FALSE', 'NASTY', 'START', 'CHILL', 'BROAD', 'TRASH', 'WAGES', 'KNIFE', 'LEARN', 'PRICE', 'ALERT', 'WITCH', 'ISSUE', 'WOMAN', 'CARRY', 'SERVE', 'ANGEL', 'DADDY', 'CLARK', 'WHOSE', 'CRIED', 'UPPER', 'GUIDE', 'SPARE', 'DOZEN', 'TIMES', 'PLANT', 'WORST', 'MOUSE', 'DRUNK', 'BADLY', 'STONE', 'HARRY', 'EXTRA', 'SHINE', 'VOICE', 'NANCY', 'CROWD', 'MEDIA', 'CAUSE', 'CIVIL', 'DROVE', 'MAYOR', 'DEATH', 'SLEPT', 'SHADE', 'FORUM', 'DRAFT', 'LUCKY', 'DERBY', 'LINKS', 'PANIC', 'MAGIC', 'PRIOR', 'BROWN', 'BLIND', 'PITCH', 'TIGER', 'BELLY', 'PLAIN', 'NOVEL', 'YOURS', 'STAMP', 'SUGAR', 'SPLIT', 'WHEEL', 'DUTCH', 'HARSH', 'OWNER', 'FRUIT', 'ALIKE', 'SUITE', 'TRUST', 'FRANK', 'SHOOT', 'HELLO', 'GRACE', 'RIGHT', 'THREE', 'OPERA', 'GROUP', 'PEARL', 'DOING', 'TEENS', 'VIDEO', 'CHUCK', 'TIRED', 'CLASS', 'TRUTH', 'DRAWN', 'FIRST', 'SHARE', 'CANAL', 'QUOTE', 'TURNS', 'WRITE', 'HIRED', 'FRAUD', 'HEAVY', 'LEGAL', 'APPLY', 'FOUND', 'VOCAL', 'LEAVE', 'BRUSH', 'WEIRD', 'EATEN', 'THICK', 'CHILD', 'RIVAL', 'STORE', 'SHORE', 'FRAME', 'HAPPY', 'STOLE', 'CRAFT', 'CROWN', 'METER', 'STAND', 'RANGE', 'THREW', 'NIGHT', 'URBAN', 'WATER', 'SHEET', 'COUNT', 'METAL', 'JEANS', 'CLICK', 'SCENE', 'USUAL', 'SIGHT', 'FLOOR', 'PHONE', 'ENEMY', 'BEAST', 'TRIED', 'BIRTH', 'ANGER', 'COURT', 'STAGE', 'CHIEF', 'SWEAR', 'TEACH', 'SAVED', 'SHIRT', 'TRULY', 'ENTRY', 'TAKEN', 'PIZZA', 'RALPH', 'CHAIR', 'ALIEN', 'BRIEF', 'SEVEN', 'PLACE', 'BOUND', 'TOUGH', 'EVENT', 'CHEAP', 'DOUBT', 'LEVEL', 'AGAIN', 'RATIO', 'FACED', 'COMIC', 'OUTER', 'FAITH', 'TRADE', 'TERRY', 'LIGHT', 'CANDY', 'CANON', 'UNTIL', 'PAINT', 'UNCLE', 'PILOT', 'PHASE'];

    function getWordListLength() public view returns (uint){
        return wordList.length;
    }
}