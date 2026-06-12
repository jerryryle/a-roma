---
title: "(August 2025) A-Roma: A 4-channel scent dispenser for harassing my boss"
---
# Background
You can find more technical detail in the [repo itself](https://github.com/jerryryle/a-roma).

I thought it would be fun to prank my boss when he came back from a two-week vacation to Italy. While he was gone, my coworkers decorated his desk with an Italian theme. I decided the desk also needed to dispense Italian-themed smells and music, so he could come home to the full sights, sounds, and scents of his trip.

![My boss's desk](media/img-desk.jpeg "Photo of my boss's desk, decorated with an Italian theme")

The night before he returned, I loaded the device with scents and mounted it under his desk.

![The device mounted under his desk](media/img-mounted.jpeg "Photo of the device mounted under his desk")

The morning my boss returned, I created a private Slack channel that included everyone in the company except him. I explained what was happening and shared a link to the device's website, where anyone could trigger a release of scent at his desk. And they did. Relentlessly. We had hours of fine Italian leather, artisan bread, espresso, and garlic. It backfired a bit: my boss was in meetings most of the day, and I was sitting downwind of his desk. But we did catch him sniffing around and asking others if they smelled something weird.

I had anticipated that he might never go looking for the source of the smells, so I'd built in an escalation feature to help him find the box: a small speaker and software to play four campy Italian songs.

After a day of gassing the office, I decided to bring it to an end. I distributed a new link that added buttons to trigger the songs. As luck would have it, I had chosen songs he'd loaded onto his own phone for the trip, so when the music started, he grabbed his phone to shut it off. Once he realized his phone wasn't the culprit, he started searching around his desk (while we madly blasted garlic), found the box, and yanked the power cord. The whole office was laughing at this point. I could hardly breathe—mostly from laughing, but also because of the garlic.

To wrap it up, I invited him into the Slack channel, where he could scroll back through a full day of plotting. I had also posted a “making of” thread there detailing how I designed and built the device. Enjoy that below.


# The Making Of
The project began with reconnaissance. I needed the dimensions of the space under the desk, and I needed to check the angle of approach to make sure the box wouldn't stick out too far or catch the eye of anyone walking up. At this point, I didn't know the desk would sport a tablecloth to help hide it.

![Checking the angle of approach](media/img-measuring-ryans-desk-approach.jpeg "Photo of my boss's desk as one would walk up to it")

![Measuring how much space I had to work with](media/img-measuring-ryans-desk.jpeg "Photo of holding a tape measure under the desk")

Next, I had to find fans that were small and quiet but still moved a reasonable amount of air.

![I got an assortment of fan sizes](media/img-fan-sizing.jpeg "Photo of fans of varying size")

(That tiny 12mm fan was ridiculous. It could barely annoy a flea.)

I settled on a 30mm square fan with a high flow rate, low noise, and low current.

![Inspecting relevant fan specifications](media/img-digikey-fan.png "Screenshot of DigiKey page with voltage, size, width, air flow, noise, and current rating circled")

With a fan chosen, I modeled an aroma channel, anchoring the design around the fan's dimensions.

![Drawing of the aroma channel](media/2D-chassis-channel.png "Screenshot of a 2D CAD drawing of the aroma channel")

![Drawing of the fan cutout and mounting holes](media/2D-chassis-fan.png "Screenshot of a 2D CAD drawing of the fan cutout and mounting holes")

For the scents themselves, I found aromatherapy oil pads that were roughly the same size as the fans.

![Aromatherapy pads](media/img-aromatherapy-pads.png "Photo of stacks of aromatherapy pads")

Then I modeled a holder for them.

![Pad holder](media/3D-filter-holder.png "Screenshot of a 3D CAD rendering of the pad holder")

![Pad holder section analysis](media/3D-filter-holder-section-analysis.png "Screenshot of a 3D CAD rendering of the pad holder, sliced to show how the two halves mate")

The full chassis is an array of four of these channels, plus a separate compartment for the electronics.

![Chassis](media/3D-chassis.png "Screenshot of a 3D CAD rendering of the chassis")

![Chassis section analysis](media/3D-chassis-section-analysis.png "Screenshot of a 3D CAD rendering of the pad holder, sliced to show the channel details")

I printed the chassis, lid, and oil pad holders in PETG, one of the more oil-resistant plastics that's not too difficult to 3D print.

![Chassis print preparation](media/bambu-3dprint-chassis.png "Screenshot of the Chassis in Bambu Studio")

![Lid print preparation](media/bambu-3dprint-lid.png "Screenshot of the Lid in Bambu Studio")

![Pad holder print preparation](media/bambu-3dprint-filter-holder.png "Screenshot of the Pad Holders in Bambu Studio")

Everything was printed on a Bambu Lab H2D, which records time lapses of its prints.

[![Chassis](media/img-print-chassis-final.jpeg "Time lapse video of the Chassis 3D printing")](https://youtu.be/BnPhF0Df4So)

[![Lid](media/img-print-lid-final.jpeg "Time lapse video of the Lid 3D printing")](https://youtu.be/3ELbYYBSLHE)

[![Pad holder](media/img-print-filter-holder-final.jpeg "Time lapse video of the Pad Holders 3D printing")](https://youtu.be/F5UshDJUx3w)


The electronics are a Raspberry Pi Zero 2 W with a hand-soldered protoboard on top to drive the fans. I couldn't quickly find an existing Raspberry Pi HAT suited to this application, so I made my own.

![Fan drive schematic](media/img-schematic.jpeg "Photo of a hand-drawn schematic")

![Wiring everything up](media/img-assembling.jpeg "Photo of the device with its wiring and circuit boards visible, next to a soldering iron")

![Assembled](media/img-assembled.jpeg "Photo of the device assembled and neater looking, with the lid off and next to the device")

Each oil pad chamber has valves over its inlet and outlet to reduce scent leakage, so I had to verify that the fans could pull them open. This video shows a smoke test of the airflow (conducted after the other smoke test: powering on my hand-soldered electronics and confirming they didn't smoke).

[![Smoke test](media/img-chassis-flow-test.jpeg "Video of me putting smoke into one of the chambers with a handheld smoke generator, covering with acrylic, and demonstrating that the fan pulls the smoke out of the chamber")](https://youtu.be/E1qMsYYkDR8)

I laser-cut a rubber gasket to help seal the chambers. I do not recommend laser-cutting rubber—it produced the worst scent in this whole adventure.

![Gasket laser cut preparation](media/bambu-laser-cut-gasket.png "Screenshot of the gasket in Bambu Suite")

The web app is a Python back end running on the Raspberry Pi, with a static HTML front end styled with Tailwind CSS. I largely vibe-coded the HTML by giving Cursor this mock-up image. The back end took more hand-coding, since Cursor kept generating garbage there.

![Mock-up I created in Photoshop](media/web-ui-mock.png "Image of a website mock-up with 4 buttons representing different scents")

![The final website](media/web-ui-basic.png "Screenshot of a website with 4 buttons to dispense different scents")

![The final website - escalation edition](media/web-ui-escalate.png "Screenshot of a website with 4 buttons to dispense different scents and 4 buttons to play different songs")

Finally, I oiled it up before installing it.

![Oiling up](media/img-oiling-up.jpeg "Photo of the device, fully assembled, with four oil jars behind it")

Then I mounted it under his desk with two screws and washers.

![Mounted](media/img-mounted.jpeg "Photo of the device, assembled and mounted under the desk")

This was a ridiculously fun project that kept my nights and weekends occupied for a couple of weeks—and it was worth every whiff of garlic.
