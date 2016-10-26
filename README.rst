==========
 HA Relay
==========

This project is spawned by my long standing desire to be able to make
my Logitech Harmony One remote do more complicated things in my living
room.

For instance, my Yamaha receiver is largely used to play internet
radio stations, but the IR based navigation for those is really
flakey. As of Home Assistant 0.31 you can now build HA script stanzas
that directly play internet radio stations. So... how can I get my
Harmony to talk to my HA instance?

Solution:

  - A raspberry pi
  - A flirc usb device (translates IR codes to key codes)
  - This code

This means a raspberry pi hanging out in the living room now acts as a
relay. By adding a Microsoft Media Center device to my Harmony profile,
and mapping those keys through flirc, I can now send a whole wide
range of additional commands and control all kinds of things in my
living room.

Yay!

This is massively specific to my environment, but made open source in
case anyone else wants to learn from it.
